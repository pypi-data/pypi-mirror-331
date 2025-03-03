import pathlib
import logging
import kalpaa.config
import typing


def set_up_logging(
	config: kalpaa.config.Config,
	log_stream: bool,
	log_file: typing.Optional[str],
	create_logfile_parents: bool = True,
):
	handlers: typing.List[logging.Handler] = []
	if log_stream:
		handlers.append(logging.StreamHandler())
	if log_file is not None:
		if create_logfile_parents:
			# create any parent directories for the log file if needed.
			pathlib.Path(log_file).parent.mkdir(parents=True, exist_ok=True)
		handlers.append(logging.FileHandler(log_file))
	logging.basicConfig(
		level=logging.DEBUG,
		format=config.general_config.log_pattern,
		handlers=handlers,
	)
	logging.getLogger("pdme").setLevel(logging.ERROR)
	logging.captureWarnings(True)
