from __future__ import annotations

import logging.config

from gooey import Gooey
from gooey import GooeyParser

from deidcm.utils import parse_log_config
from deidcm.deidentifier import Deidentifier

####### FIX ######
# following redirects stdout to stderr
# and prevents GUI hanging
# see https://github.com/chriskiehl/Gooey/issues/520
import sys
import codecs

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
##################


logging.config.dictConfig(parse_log_config())
log = logging.getLogger(__name__)


@Gooey(dump_build_config=False, program_name="DICOM De-Identifier Tool")
def gui_generator() -> None:
    """Generates minimal GUI, creates and runs deidentifier object with args."""

    description = "made for Gore by Tuguldur."
    help_msg = "Click on Browse and select the directory destination containing DICOM data."

    parser = GooeyParser(description=description)

    parser.add_argument(
        "InputDirectory", 
        help=help_msg, 
        widget="DirChooser"
        )

    parser.add_argument(
        '-b', '--bundled_output',
        metavar='Output Format',
        action='store_true',
        help='Check this box if you want to bundle all de-identified data in a separate "Deidentified" folder.')    

    args = parser.parse_args()

    Deidentifier.create(args).run()


if __name__ == '__main__':
	gui_generator()
