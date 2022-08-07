from __future__ import annotations

import os
import logging
from pathlib import Path

from tqdm import tqdm
from pydicom.misc import is_dicom

from deidcm.validation import Validator


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

	def process(self, item: str) -> None:
		"""."""
		item_path = Path(f'{self.input_directory}/{item}')
		item_is = Validator(item_path).check()
		log.info(f'{item_is}')
		#if item_is.dicom:
		#	if not item_is.dir and not item_is.compressed:
		#		self.instance.deidentify(item_path)
		#	if item_is.dir:
		#		self.directory.deidentify(item_path)
		#	if not item_is.dir and item_is.compressed:
		#		self._process_compressed(item_path)

	def processX(self, item: str|Path) -> None:
		"""."""
		item_path = Path(f'{self.input_directory}/{item}')
		if item_path.is_file():
			if is_dicom(item_path):
				log.info(f'item: {item} is a DICOM file')
				#self.instance.deidentify(item_path)
			fname, _ = os.path.splittext(item_path)
			try:
				shutil.unpack_archive(item_path)
				log.info(f'item: {item} is a compressed file')
				dir_path = f'{self.input_directory}/{fname}_deidentified'
				shutil.move(f'{self.input_directory}/{fname}', dir_path)
				log.info(f'decompressed to: {dir_path}')
				if Path(dir_path).is_file() and is_dicom(dir_path):
					log.info('decompressed file is DICOM')
					self.instance.deidentify(dir_path)
				elif Path(dir_path).is_file and not is_dicom(dir_path):
					log.info('decompressed file not DICOM, removed')
					os.remove(dir_path)
				else:
					self.directory.deidentify(dir_path)
					shutil.make_archive(dir_path)
			except ValueError:
				log.info(f'item: {item} is not DICOM data')
		if item_path.is_dir():
			self.directory.deidentify(item_path)

	def run(self) -> None:
		"""Processes each item in input directory, and bundles the outputs if applicable."""
		items = os.listdir(self.input_directory)
		log.info(f'processing {len(items)} items')
		for item in tqdm(items, total=len(items)):
			self.process(item)
		if self.bundled_output:
			...
			#output_bundler() <--- from utils
