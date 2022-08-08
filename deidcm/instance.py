from __future__ import annotations

import logging
from pathlib import Path

from pydicom import dcmread

from deidcm.utils import parse_tag_config


log = logging.getLogger(__name__)


class Instance:
	"""Deidentifies a given DICOM instance.

	Attributes
	----------
	path: Path
		Path to DICOM instance.
	tags: list
		List of tag names to be de-identified.

	Methods
	-------
	deidentify()
		Reads header until pixel_data and recursively nulls values of de-identification tag list.
	"""
	def __init__(self, dicom_path: Path) -> None:
		self.path = dicom_path
		self.tags = parse_tag_config()

	def _recursive_edit(self, header: pydicom.FileDataSet, tag_name: str) -> pydicom.FileDataSet:
		"""Recursively edits inplace all occurences of given tag value.

		Parameters
		----------
		header: pydicom.FileDataSet
			Parsed DICOM header including pixel data.
		tag_name: str
			Standard space-less tag name to be nulled.

		Returns
		-------
		header: pydicom.FileDataSet
			De-identified header.
		"""
		for elem in header:
			if elem.VR == 'SQ':
				[self._recursive_edit(item, tag_name) for item in elem]
			else:
				if elem.tag == tag_name:
					elem.value = ''
		return header

	def deidentify(self) -> None:
		"""Performs instance de-identification."""
		with dcmread(self.path) as header:
			for tag in self.tags:
				self._recursive_edit(header, tag)
			header.save_as(self.path)