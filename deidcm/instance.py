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
		self.tags = parse_tag_config('keep')

	def _filter_tags(self, header: pydicom.FileDataSet) -> None:
		"""Filters base level tags and removes if it does not exist in keep-list.

		Parameters
		----------
		header: pydicom.FileDataSet
			Parsed DICOM header including pixel data.
		"""
		for elem in header:
			if elem.tag not in self.tags:
				del header[elem.tag]

	def _recursive_edit(self, header: pydicom.FileDataSet, tag_name: str) -> None:
		"""Recursively edits inplace all occurences of given tag value.

		Parameters
		----------
		header: pydicom.FileDataSet
			Parsed DICOM header including pixel data.
		tag_name: str
			Standard space-less tag name to be nulled.
		"""
		for elem in header:
			if elem.VR == 'SQ':
				[self._recursive_edit(item, tag_name) for item in elem]
			else:
				if elem.tag == tag_name:
					del header[elem.tag]

	def _private_edit(self, header: pydicom.FileDataSet) -> None:
		"""Nulls all private tag values in place."""
		for elem in header:
			if elem.tag.group % 2 != 0:
				elem.value = ''

	def deidentify(self, priv_tag_flag: bool) -> None:
		"""Performs instance de-identification.

		Parameters
		----------
		priv_tag_flag: bool
			If true all private tags are untouched. If false all of them nulled.
		"""
		with dcmread(self.path) as header:
			log.info(f'---> {self.path}')
			# For keep list
			self._filter_tags(header)
			# For remove list
			#for tag in self.tags:
			#	self._recursive_edit(header, tag)
			if not priv_tag_flag:
				header.remove_private_tags()
			header.save_as(self.path)
