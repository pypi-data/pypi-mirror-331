import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from blue_flie import NAME
from blue_flie.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="",
)
args = parser.parse_args()

success = False
if args.task == "task":
    success = False
else:
    success = None

sys_exit(logger, NAME, args.task, success)
