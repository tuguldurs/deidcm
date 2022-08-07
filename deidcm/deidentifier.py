from __future__ import annotations

import os
import shutil
import logging
from pathlib import Path

from tqdm import tqdm
from pydicom.misc import is_dicom

from deidcm.validation import Validator
from deidcm.instance import Instance


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
		if item_is.dicom:
			if not item_is.dir and not item_is.compressed:
				fname, ext = os.path.splitext(item)
				dicom_path = Path(f'{fname}_deidentified{ext}')
				shutil.copy(item_path, dicom_path)
				Instance(dicom_path).deidentify()
		#		self.instance.deidentify(item_path)
		#	if item_is.dir:
		#		self.directory.deidentify(item_path)
		#	if not item_is.dir and item_is.compressed:
		#		self._process_compressed(item_path)

	def run(self) -> None:
		"""Processes each item in input directory, and bundles the outputs if applicable."""
		items = os.listdir(self.input_directory)
		log.info(f'processing {len(items)} items')
		for item in tqdm(items, total=len(items)):
			self.process(item)
		if self.bundled_output:
			...
			#output_bundler() <--- from utils
