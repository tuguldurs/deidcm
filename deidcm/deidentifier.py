from __future__ import annotations

import os
import glob
import shutil
import base64
import hashlib
import logging
from pathlib import Path

from tqdm import tqdm
from pydicom.misc import is_dicom

from deidcm.validation import Validator
from deidcm.instance import Instance
from deidcm.dicomdir import DicomDir
from deidcm.utils import clean
from deidcm.utils import clean_old_output
from deidcm.utils import output_bundler


log = logging.getLogger(__name__)


__all__ = ['deidentifier']


class Deidentifier:
	"""
	Driver class.

	Methods
	-------
	create()
		Creates deidentifier object with input args as attributes.
	process()
		Identifies type of each input item and calls appropriate processing routines.
	run()
		Cleans any old output directories, and iterates processing through each item of input directory.
	"""
	
	@classmethod
	def create(cls, args: argparse.ArgumentParser) -> deidentifier:
		"""Creates a deidentifier object."""
		setattr(cls, 'input_directory', args.InputDirectory)
		setattr(cls, 'no_bundled_output', args.no_bundled_output)
		setattr(cls, 'skip_private_tags', args.skip_private_tags)
		deidentifier = cls()
		log.info(f'deidentifier object created to process: {cls.input_directory}')
		return deidentifier

	def _deidentify_dicomdir(self, item_path) -> None:
		"""Process DICOMDIR file."""
		dicom_path = Path('DICOMDIR')
		shutil.copy(item_path, dicom_path)
		DicomDir(dicom_path).deidentify()

	def _deidentify_file(self, full_file_name: str, item_path: Path) -> None:
		"""Processes plain DICOM file."""
		fname, ext = os.path.splitext(full_file_name)
		dicom_path = Path(f'{fname}_deidentified{ext}')
		shutil.copy(item_path, dicom_path)
		Instance(dicom_path).deidentify(self.skip_private_tags)

	def _get_hash_oneway(self, somestring: str) -> str:
		"""Sha256 hash value."""
		h = hashlib.new('sha256')
		h.update(somestring.encode())
		return h.hexdigest()

	def _get_encode(self, somestring: str) -> str:
		"""Base64 encoding."""
		return base64.b64encode(somestring.encode('ascii')).decode('ascii')

	def _deidentify_dir(self, dir_name: str, item_path: Path) -> str:
		"""Processes directory containing DICOM data."""
		#dir_name = self._get_encode(dir_name)
		dir_path = Path(f'{dir_name}_deidentified')
		shutil.copytree(item_path, dir_path)

		for item in os.listdir(dir_path):
			subitem_path = Path(f'{dir_path}/{item}')
			if subitem_path.is_dir():
				subitem_is = Validator(subitem_path).check()
				if subitem_is.dicom:
					new_name = self._get_encode(item)
					shutil.move(subitem_path, f'{dir_path}/{new_name}')
		
		for path_to_file in glob.glob(str(dir_path) + '**/**', recursive=True):
			if path_to_file.split('/')[-1] == 'DICOMDIR':
				DicomDir(path_to_file).deidentify()
				continue
			if Path(path_to_file).is_file() and is_dicom(path_to_file):
				Instance(path_to_file).deidentify(self.skip_private_tags)
		return dir_name

	def _deidentify_compressed(self, item: str, item_path: Path) -> None:
		"""Processes compressed files."""
		fname, ext = os.path.splitext(item)
		shutil.unpack_archive(item_path)
		if Path(fname).is_file():
			self._deidentify_file(fname, Path(fname))
		else:
			new_name = self._deidentify_dir(fname, Path(fname))
		shutil.make_archive(f'{new_name}_deidentified', ext[1:], f'{new_name}_deidentified')
		clean(Path(fname))
		clean(Path(f'{new_name}_deidentified'))

	def process(self, item: str) -> None:
		"""Determined item type and calls individual processing methods for each type.

		DICOMDIR file is processed separately.

		Parameters
		----------
		item: str
			Full file/dir name of processing item.
		"""
		item_path = Path(f'{self.input_directory}/{item}')
		item_is = Validator(item_path).check()
		if item == 'DICOMDIR':
			item_is.dicom = True
			log.info(f'{item} --- {item_is}')
			self._deidentify_dicomdir(item_path)
			return
		log.info(f'{item} --- {item_is}')
		if item_is.dicom:
			if not item_is.dir and not item_is.compressed:
				self._deidentify_file(item, item_path)				
			if item_is.dir:
				self._deidentify_dir(item, item_path)
			if item_is.compressed:
				self._deidentify_compressed(item, item_path)

	def run(self) -> None:
		"""Processes each item in input directory, and bundles the outputs if applicable."""
		clean_old_output(self.input_directory)
		items = os.listdir(self.input_directory)
		log.info(f'processing {len(items)} items')
		for item in tqdm(items, total=len(items)):
			self.process(item)
			log.info(f'{item} <--- deidentified.')
		if not self.no_bundled_output:
			output_bundler(self.input_directory)
