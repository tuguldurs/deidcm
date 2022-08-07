from __future__ import annotations

import os
import json
import shutil
from pathlib import Path


from . import package_config_path


def parse_log_config() -> dict:
	"""Parses logging config."""

	config_file = f'{package_config_path}/logger.json'

	with open(config_file) as handler:
		configuration = json.load(handler)

	return configuration

def clean(path_to_item: Path) -> None:
	"""Deletes item, either file or dir."""
	if path_to_item.is_file():
		os.remove(path_to_item)
	else:
		shutil.rmtree(path_to_item)