import sys
import fitz


class SfRedactor:

    def __init__(self, path):
        self.path = path
        self.sf = fitz.open(self.path)

    def redact(self, savename):
        """."""
        for idx, page in enumerate(self.sf):
            if idx > 0:
                self.sf.delete_page(idx+1)
                break
            lines = page.get_text('text').split('\n')
            kwd = ''
            for idx_line, line in enumerate(lines):
                if 'Patient ID' in line or 'Account' in line or 'Physician' in line or 'Date' in line:
                    kwd = line
                if kwd:
                    areas = page.search_for(kwd)
                    [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas]
                    page.apply_redactions()
        self.sf.save(savename)
