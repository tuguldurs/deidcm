from __future__ import annotations

import shutil
import logging
from pathlib import Path

from pydicom.misc import is_dicom

from .utils import clean


log = logging.getLogger(__name__)


class Validator:
	"""Checks the item from input directory to determine if it is/has DICOM data.

	Methods
	-------
	check: ...
		...
	"""
	def __init__(self, item_path: Path) -> None:
		self.path = item_path
		self.dir = False if self.path.is_file() else True
		self.compressed = self._get_compressed()

	def _get_compressed(self) -> bool:
		"""Checks if item is a compressed file."""
		if self.dir:
			return False
		try:
			shutil.unpack_archive(self.path)
			clean(self.path)
			return True
		except (shutil.ReadError, ValueError):
			return False

	def _check_file_dicom(self):
		"""Checks if file is DICOM."""
		if is_dicom(self.path):
			return True
		return False

	def check(self) -> dict:
		"""."""
		if not self.dir and not self.compressed:
			dicom = self._check_file_dicom()
		return {'dir': self.dir, 'compressed': self.compressed, 'dicom': dicom}
