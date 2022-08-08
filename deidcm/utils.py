from __future__ import annotations

import os
import json
import shutil
from pathlib import Path

from . import package_config_path


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

def make_archive(source, destination):
	base = os.path.basename(destination)
	name = base.split('.')[0]
	fmt = base.split('.')[1]
	archive_from = os.path.dirname(source)
	archive_to = os.path.basename(source.strip(os.sep))
	shutil.make_archive(name, fmt, archive_from, archive_to)
	shutil.move('%s.%s'%(name, fmt), destination)