from __future__ import annotations

import logging
from pathlib import Path

from pydicom import dcmread

from deidcm.utils import parse_tag_config


log = logging.getLogger(__name__)


class DicomDir:
	"""Deidentifies a given DICOMDIR instance file.

	Unlike regular DICOM instances, the DICOMDIR file does not contain any PHI in its 
	base level tags. However some PHI tags can be listed in the top sections of 
	Directory Record Seqeuence. All existing PHI tags are removed entirely within the sequence.

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
		self.tags = parse_tag_config()

	def _remove_tags(self, header: pydicom.FileDataSet) -> None:
		"""Removes PHI tags within the first two members of (0004, 1220) sequence.

		Parameters
		----------
		header: pydicom.FileDataSet
			Parsed DICOMDIR header.
		"""
		for member in range(2):
			for elem in header[0x0004, 0x1220][member]:
				if elem.tag in self.tags:
					del header[0x0004, 0x1220][member][elem.tag]

	def deidentify(self, priv_tag_flag: bool) -> None:
		"""Performs DICOMDIR de-identification."""
		with dcmread(self.path) as header:
			log.info(f'---> {self.path}')
			self._remove_tags(header)
			header.save_as(self.path)
