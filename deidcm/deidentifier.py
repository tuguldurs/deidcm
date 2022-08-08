from __future__ import annotations

import os
import glob
import shutil
import logging
from pathlib import Path

from tqdm import tqdm
from pydicom.misc import is_dicom

from deidcm.validation import Validator
from deidcm.instance import Instance
from deidcm.utils import clean
from deidcm.utils import make_archive


log = logging.getLogger(__name__)


__all__ = ['deidentifier']


class Deidentifier:
	"""..."""
	
	@classmethod
	def create(cls, args: argparse.ArgumentParser) -> deidentifier:
		"""Creates a deidentifier object."""
		setattr(cls, 'input_directory', args.InputDirectory)
		setattr(cls, 'bundled_output', args.bundled_output)
		deidentifier = cls()
		log.info(f'deidentifier object created to process: {cls.input_directory}')
		return deidentifier

	def _deidentify_file(self, full_file_name: str, item_path: Path) -> None:
		"""Processes plain DICOM file."""
		fname, ext = os.path.splitext(full_file_name)
		dicom_path = Path(f'{fname}_deidentified{ext}')
		shutil.copy(item_path, dicom_path)
		Instance(dicom_path).deidentify()

	def _deidentify_dir(self, dir_name: str, item_path: Path) -> None:
		"""Processes directory containing DICOM data."""
		dir_path = Path(f'{dir_name}_deidentified')
		shutil.copytree(item_path, dir_path)
		for path_to_file in glob.glob(str(dir_path) + '**/**', recursive=True):
			if Path(path_to_file).is_file() and is_dicom(path_to_file):
				Instance(path_to_file).deidentify()

	def process(self, item: str) -> None:
		"""."""
		item_path = Path(f'{self.input_directory}/{item}')
		item_is = Validator(item_path).check()
		if item_is.dicom:
			if not item_is.dir and not item_is.compressed:
				self._deidentify_file(item, item_path)				
			if item_is.dir:
				self._deidentify_dir(item, item_path)
			if item_is.compressed:
				fname, ext = os.path.splitext(item)
				shutil.unpack_archive(item_path)
				if Path(fname).is_file():
					self._deidentify_file(fname, Path(fname))
				else:
					self._deidentify_dir(fname, Path(fname))
				shutil.make_archive(f'{fname}_deidentified', ext[1:], f'{fname}_deidentified')
				clean(Path(fname))
				clean(Path(f'{fname}_deidentified'))

	def run(self) -> None:
		"""Processes each item in input directory, and bundles the outputs if applicable."""
		items = os.listdir(self.input_directory)
		log.info(f'processing {len(items)} items')
		for item in tqdm(items, total=len(items)):
			self.process(item)
		if self.bundled_output:
			...
			#output_bundler() <--- from utils
