from __future__ import annotations

import glob
import shutil
import logging
from pathlib import Path
from collections import namedtuple

from pydicom.misc import is_dicom

from deidcm.utils import clean
from deidcm.utils import decompressed_path


log = logging.getLogger(__name__)


class Validator:
	"""Checks the item from input directory to determine if it is/has DICOM data.

	Supports following:
	 - plain or compressed individual DICOM files (does not need to have .dcm extension)
	 - compressed study/series with or without DICOMDIR and/or viewer executables
	 - plain study/series directories

	Unsupported:
	 - if for some reason the decompressed dir contains compressed content

	Attributes
	----------
	path: Path
		Path to input directory item.
	dir: bool
		Whether item is a directory.
	compressed: bool
		Whether item is a compressed file.

	Methods
	-------
	check()
		Evaluates input directory item and creates a namedtuple with its attributes. 
	"""
	def __init__(self, item_path: Path) -> None:
		self.path = item_path
		self._decompressed_path = decompressed_path(self.path)
		self.dir = False if self.path.is_file() else True
		self.compressed = self._get_compressed()

	def _get_compressed(self) -> bool:
		"""Checks if item is a compressed file.

		ReadError is raised when its not a compressed file.
		ValueError should raise if it does not contain any of the supported extensions.
		"""
		if self.dir:
			return False
		try:
			shutil.unpack_archive(self.path)
			clean(self._decompressed_path)
			return True
		except (shutil.ReadError, ValueError):
			return False

	def _check_file_dicom(self, decompressed: bool = False) -> bool:
		"""Checks if file is DICOM."""
		path_to_file = self.path if not decompressed else self._decompressed_path
		if is_dicom(path_to_file):
			return True
		return False

	def _check_dir_dicom(self, decompressed: bool = False) -> bool:
		"""Checks if directory contains any DICOM."""
		path_to_dir = self.path if not decompressed else self._decompressed_path
		for path_to_file in glob.glob(str(path_to_dir) + '**/**', recursive=True):
			if Path(path_to_file).is_file() and is_dicom(path_to_file):
				return True
		return False

	def check(self) -> namedtuple:
		"""Checks whether input directory item is file vs dir, compressed or not, and is/has valid DICOM data in it."""
		Item = namedtuple('Item', 'path dir compressed dicom')
		if not self.dir and not self.compressed:
			dicom = self._check_file_dicom()
		if self.dir:
			dicom = self._check_dir_dicom()
		if self.compressed:
			shutil.unpack_archive(self.path)
			if self._decompressed_path.is_file():
				dicom = self._check_file_dicom(decompressed=True)
			else:
				dicom = self._check_dir_dicom(decompressed=True)
			clean(self._decompressed_path)
		return Item(self.path, self.dir, self.compressed, dicom)
