from __future__ import annotations

import json

from . import package_config_path


def parse_log_config() -> dict:
	"""Parses logging config."""

	config_file = f'{package_config_path}/logger.json'

	with open(config_file) as handler:
		configuration = json.load(handler)

	return configuration
