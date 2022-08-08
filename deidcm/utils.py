from __future__ import annotations

import os
import json
import shutil
import logging
from pathlib import Path

from . import package_config_path


log = logging.getLogger(__name__)


def parse_log_config() -> dict:
	"""Parses logging config."""
	with open(f'{package_config_path}/logger.json') as handler:
		configuration = json.load(handler)
	return configuration


def clean(path_to_item: Path) -> None:
	"""Deletes item, either file or dir."""
	if path_to_item.is_file():
		os.remove(path_to_item)
	else:
		shutil.rmtree(path_to_item)


def decompressed_path(compressed_path: Path) -> Path:
	"""Parses path to decompressed file/dir, assuming compressed path ends with a file with extension."""
	return Path('.'.join(str(compressed_path).split('\\')[-1].split('.')[:-1]))


def parse_tag_config() -> list:
	"""Parses tags to de-identify."""
	with open(f'{package_config_path}/tags.txt', 'r') as handler:
		lines = handler.readlines()
	return [line.strip() for line in lines if line[0] != '#']


def clean_old_output(input_dir: Path) -> None:
	"""Removed old output directories."""
	paths = [Path('deidentified'), Path(f'{input_dir}/deidentified')]
	for path_to_clean in paths:
		if path_to_clean.is_dir():
			shutil.rmtree(path_to_clean)
			log.info(f'old results removed at: {path_to_clean}')


def output_bundler(input_dir: Path) -> None:
	"""Bundles outputs into a directory and move to input directory."""
	os.mkdir('deidentified')
	for item in os.listdir('.'):
		if '_deidentified' in item:
			shutil.move(item, 'deidentified')
	shutil.move('deidentified', input_dir)
	log.info(f'deidentified data ready at: {input_dir}/deidentified')
