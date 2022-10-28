from __future__ import annotations

from dateutil.parser import parse

from fitz import open as openpdf
from fitz import Page
from fitz import Document


class SfRedactor:
    """Redacts Selection/Screening form PDF file for PHI.

    Supports two distinct versions - pre/after ~2020.

    Attributes
    ----------
    path: str
        Path to input SF file.
    sf: Document
        Parsed SF file.
    redact_kwds: dict
        Version dependent keywords to be used to located redaction lines.
    """

    def __init__(self, path: str):
        self.path = path
        self.sf = openpdf(self.path)
        self.delete_pages()
        self.redact_kwds = {'new': ['Patient ID', 'Case Date'],
                            'old': ['Patient Name', 'Procedure Date']}

    @staticmethod
    def _check_kwd_in_page(kwd: str, lines: list) -> bool:
        """Checks whether given keyword exists in parsed text lines.

        Parameters
        ----------
        kwd: str
            Keyword(s) to search.
        lines: list
            All parsed lines.

        Returns
        -------
            True if keyword(s) is found, False if not.
        """
        for line in lines:
            if kwd.upper() in line.upper():
                return True
        return False

    def get_sf_version(self, lines: list) -> str:
        """Identifies SF file version.

        New files have 'Selection Form' somewhere in the title, while the old versions have 'Screening Form'.

        Parameters
        ----------
        lines: list
            All parsed lines.

        Returns
        -------
        : str
            'new' for new version file, or 'old' for old version.

        Raises
        ------
        SystemExit
            If the input file is not recognized to be new or old version.
        """
        if self._check_kwd_in_page('selection form', lines):
            return 'new'
        elif self._check_kwd_in_page('screening form', lines):
            return 'old'
        else:
            print('SF file version not recognized')
            raise SystemExit

    def delete_pages(self, idx_min: int = 0) -> None:
        """Removes all pages in-place from the document past the minimum index."""
        idxs_to_remove = [i for i in range(len(self.sf)) if i > idx_min]
        self.sf.delete_pages(idxs_to_remove)

    @staticmethod
    def get_lines(page: Page) -> list:
        """Extracts all lines from page text.

        Parameters
        ----------
        page: Page
            Single page parsed document.

        Returns
        -------
        : list
            All non-empty lines.
        """
        lines = page.get_text('text').split('\n')
        return [line.strip() for line in lines if line]

    def get_redact_idxs(self, redact_kwds: list, lines: list) -> tuple:
        """Locates start and end indices of redaction lines.

        The end index may or may not be of the line containing end keyword. The next line is checked 
        whether it is a parse-able datetime string; if yes, then the end index will be of that line
        containing the datetime string.

        Parameters
        ----------
        redact_kwds: list[str, str]
            Start and end keywords to be searched with.
        lines: list
            All parsed lines.

        Returns
        -------
        : tuple[int, int]
            Start and end indices of lines to be redacted.
        """
        redact_kwd_start, redact_kwd_end = redact_kwds
        idx_start, idx_end = 0, 0
        for idx, line in enumerate(lines):
            if redact_kwd_start in line:
                idx_start = idx
                break
        for idx, line in enumerate(lines):
            if redact_kwd_end in line:
                idx_end = idx
                try:
                    parse(lines[idx])
                    idx_end = idx+1
                except ValueError:
                    ...
                break
        return idx_start, idx_end

    def redact(self, savename: str) -> None:
        """Performs PDF redaction.

        Parameters
        ----------
        savename: str
            Full file name to save the modified PDF file as.
        """
        for i,page in enumerate(self.sf):
            lines = self.get_lines(page)
            redact_kwds = self.redact_kwds[self.get_sf_version(lines)]
            idx_start, idx_end = self.get_redact_idxs(redact_kwds, lines)
            for idx in range(idx_start, idx_end+1):
                if lines[idx]:
                    areas = page.search_for(lines[idx])
                    [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
                    page.apply_redactions()
        self.sf.save(savename)
