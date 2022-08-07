from __future__ import annotations

import os
import logging

from tqdm import tqdm


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

	def process(self, item: str|Path) -> None:
		...

	def output_bundler(self) -> None:
		...

	def run(self) -> None:
		"""Processes each item in input directory, and bundles the outputs if applicable."""
		items = os.listdir(self.input_directory)
		log.info(f'processing {len(items)} items')
		for item in tqdm(items, total=len(items)):
			self.process(item)
		if self.bundled_output:
			self.output_bundler()
