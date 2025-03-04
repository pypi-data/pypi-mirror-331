import pathlib
import kalpaa.config
import logging
from enum import Enum
import filecmp

_logger = logging.getLogger(__name__)

KALPAA_COMPLETE = "kalpaa.complete"
COMPLETIONS_DIR = "completions"

# let us implement our own stuff later, this just handles checking if a thing exists or not.


class CompletionsStatus(Enum):
	NOT_COMPLETE = "not_complete"
	INVALID = "invalid"
	COMPLETE = "complete"


def _cwd_file_matches_previous(root_dir: pathlib.Path, file_name: str) -> bool:
	"""
	Compare the file in the current working directory with the file in the target root.

	Returns true if they match (meaning continuation is possible), false otherwise.

	Should do byte-by-byte comparison

	:param cwd_file_name: the file name in the current working directory
	:param root_file_name: the file name in the target root
	:return: True if the files match, False otherwise
	"""
	current_file = pathlib.Path.cwd() / file_name
	copied_file = root_dir / file_name

	result = filecmp.cmp(current_file, copied_file, shallow=False)
	_logger.debug(f"Compared {current_file} with {copied_file}, got {result}")
	return result


def check_completion_file(config: kalpaa.Config, filename: str) -> CompletionsStatus:
	"""
	Check if the completion file exists for a given filename.

	:param config: the config object
	:param filename: the filename to check
	:return: the completion status
	"""
	if not config.general_config.check_completions:
		_logger.debug("Not checking completions")
		return CompletionsStatus.NOT_COMPLETE

	root_dir = config.general_config.root_directory
	completions_dir = root_dir / COMPLETIONS_DIR

	# completions_dir.mkdir(exist_ok=True, parents=True)
	if not completions_dir.is_dir():
		_logger.debug(
			f"Completions dir {completions_dir=} does not exist and it should, invalid!"
		)
		return CompletionsStatus.INVALID

	complete_file = completions_dir / filename
	if complete_file.exists():
		_logger.info(f"Found {complete_file}, exiting")
		return CompletionsStatus.COMPLETE
	else:
		_logger.info(f"Did not find {complete_file}, continuing")
		return CompletionsStatus.NOT_COMPLETE


def set_completion_file(config: kalpaa.Config, filename: str):
	"""
	Set the completion file for a given filename.

	:param config: the config object
	:param filename: the filename to set
	"""
	if not config.general_config.check_completions:
		_logger.debug("Not checking completions or setting them")
		return
	root_dir = config.general_config.root_directory
	completions_dir = root_dir / COMPLETIONS_DIR
	completions_dir.mkdir(exist_ok=True, parents=True)
	complete_file = completions_dir / filename
	complete_file.touch()
	_logger.info(f"Set {complete_file}")


def check_initial_completions(
	config_file: str, config: kalpaa.Config
) -> CompletionsStatus:
	"""
	Check if the completion files exist.

	First check if the out dir has been created.
	If not, then we can run as normal.

	If the out dir exists, check whether the config file matches the one we are using.
	If not, we have an invalid case and should error (don't want to change settings when resuming!).

	Finally, check whether a kalpaa.complete file exists, and if so then exit.
	"""

	root_dir = config.general_config.root_directory
	_logger.debug(f"Checking completions for {root_dir=}")

	if not config.general_config.check_completions:
		_logger.debug("Not checking completions")
		return CompletionsStatus.NOT_COMPLETE
	if not root_dir.is_dir():
		_logger.debug(f"Root dir {root_dir} does not exist, continuing")
		return CompletionsStatus.NOT_COMPLETE

	# check if the config file matches

	files_to_check = [
		config.general_config.indexes_json_name,
		config.general_config.dots_json_name,
		config_file,
	]

	for file in files_to_check:
		if (root_dir / file).exists():
			_logger.info(f"Checking {file}, which exists")
			if not _cwd_file_matches_previous(root_dir, file):
				_logger.error(f"Config file {file} does not match copied config")
				return CompletionsStatus.INVALID
		else:
			_logger.debug(
				f"Config file {file} does not exist, expect it will be created this run"
			)

	completions_dir = root_dir / COMPLETIONS_DIR
	completions_dir.mkdir(exist_ok=True, parents=True)
	complete_file = completions_dir / KALPAA_COMPLETE
	if complete_file.exists():
		_logger.info(f"Found {complete_file}, exiting")
		return CompletionsStatus.COMPLETE
	else:
		_logger.info(f"Did not find {complete_file}, continuing")
		return CompletionsStatus.NOT_COMPLETE
