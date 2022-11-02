from __future__ import annotations

import logging
import warnings
from pathlib import Path

from pydicom import dcmread

from deidcm.utils import parse_tag_config


log = logging.getLogger(__name__)


class DicomDir:
	"""Deidentifies a given DICOMDIR instance file.

	Unlike regular DICOM instances, the DICOMDIR file does not contain any PHI in its 
	base level tags. However some PHI tags can be listed in the top records of 
	Directory Record Seqeuence. All existing PHI tags are entirely redacted within the sequence

	The redaction applies same character length string but consisting from only 0s, e.g.:
	"JOHN" becomes "0000". The sole purpose here is to preserve the native byte offsets among 
	records.


	Attributes
	----------
	path: Path
		Path to DICOMDIR instance.
	tags: list[str]
		List of tag names to be de-identified.

	Methods
	-------
	deidentify()
		Parses the entire contents and removes tags from de-identification tag list.
	"""
	def __init__(self, dicom_path: Path) -> None:
		self.path = dicom_path
		self.tags = parse_tag_config('redact')

	def _redact_tags(self, header: pydicom.FileDataSet) -> None:
		"""Redacts PHI tags within the first two records of (0004, 1220) sequence.

		Record#1: PATIENT
		Record#2: STUDY

		Parameters
		----------
		header: pydicom.FileDataSet
			Parsed DICOMDIR header.
		"""
		for record in range(2):
			for elem in header[0x0004, 0x1220][record]:
				if elem.tag in self.tags:
					log.info(f'redacting {elem.tag} in record {record+1}')
					with warnings.catch_warnings():
						warnings.simplefilter("ignore")
						elem.value = '0' * len(elem.value)

	def deidentify(self) -> None:
		"""Performs DICOMDIR de-identification."""
		with dcmread(self.path) as header:
			log.info(f'---> {self.path}')
			self._redact_tags(header)
			header.save_as(self.path)
