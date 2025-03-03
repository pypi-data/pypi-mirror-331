import pathlib
import logging

import dataclasses

import kalpaa.stages.stage01
import kalpaa.stages.stage02
import kalpaa.stages.stage03
import kalpaa.stages.stage04
import kalpaa.common
import kalpaa.config

from typing import Protocol

import kalpaa.completions

import argparse


class Runnable(Protocol):
	config: kalpaa.Config

	def run(self):
		pass


class Completable:
	def __init__(self, runnable: Runnable, completion_name: str):
		self.runnable = runnable
		self.completion_name = completion_name

	def run(self):
		_logger.info(
			f"Running {self.runnable} with completion name {self.completion_name}"
		)
		completions = kalpaa.completions.check_completion_file(
			self.runnable.config, self.completion_name
		)
		if completions == kalpaa.completions.CompletionsStatus.COMPLETE:
			_logger.info(f"Skipping {self.completion_name}")
			return
		elif completions == kalpaa.completions.CompletionsStatus.INVALID:
			_logger.error(f"Invalid completion status for {self.completion_name}")
			raise ValueError(f"Invalid completion status for {self.completion_name}")
		else:
			_logger.debug(f"Not completed for {self.completion_name}, running")
		self.runnable.run()
		_logger.info(f"Setting completion for {self.completion_name}")
		kalpaa.completions.set_completion_file(
			self.runnable.config, self.completion_name
		)


# try not to use this out side of main or when defining config stuff pls
# import numpy

_logger = logging.getLogger(__name__)


class Runner(Runnable):
	def __init__(self, config: kalpaa.Config):
		self.config = config
		_logger.info(f"Initialising runner with {config=}")

	def run(self):

		stage01 = Completable(
			kalpaa.stages.stage01.Stage01Runner(self.config), "stage01.complete"
		)
		stage02 = Completable(
			kalpaa.stages.stage02.Stage02Runner(self.config), "stage02.complete"
		)
		stage03 = Completable(
			kalpaa.stages.stage03.Stage03Runner(self.config), "stage03.complete"
		)
		stage04 = Completable(
			kalpaa.stages.stage04.Stage04Runner(self.config), "stage04.complete"
		)

		if self.config.general_config.skip_to_stage is not None:

			stages = [stage01, stage02, stage03, stage04]

			start = int(self.config.general_config.skip_to_stage)
			_logger.info(f"Received instruction to start at stage {start + 1}")
			for i, stage in enumerate(stages[start:4]):
				_logger.info(f"*** Running stage {i + start + 1}")
				stage.run()

		else:
			# standard run, can keep old

			_logger.info("*** Beginning Stage 01 ***")
			stage01.run()

			_logger.info("*** Beginning Stage 02 ***")
			stage02.run()

			_logger.info("*** Beginning Stage 03 ***")
			stage03.run()

			_logger.info("*** Beginning Stage 04 ***")
			stage04.run()
		kalpaa.completions.set_completion_file(
			self.config, kalpaa.completions.KALPAA_COMPLETE
		)


def parse_args():

	parser = argparse.ArgumentParser(
		"Multistage Runner", formatter_class=argparse.ArgumentDefaultsHelpFormatter
	)

	parser.add_argument(
		"--override-root",
		type=str,
		help="If provided, override the root dir.",
		default=None,
	)

	parser.add_argument(
		"--log-stream",
		action="store_true",
		help="Log to stream",
		default=False,
	)

	parser.add_argument(
		"-d",
		"--directory-label",
		type=str,
		help="Label for directory to put files in within root",
		default="output1",
	)

	parser.add_argument(
		"--config-file",
		type=str,
		help="kalpaa.toml file to use for configuration",
		default="kalpaa.toml",
	)

	parser.add_argument(
		"-s",
		"--skip-to-stage",
		type=int,
		help="Skip to stage, if provided. 1 means stages 1-4 will run, 4 means only stage 4 will run.",
		default=None,
	)
	args = parser.parse_args()
	return args


def main():
	args = parse_args()

	config = kalpaa.config.read_config(pathlib.Path(args.config_file))
	label = args.directory_label

	if args.override_root is None:
		_logger.info("root dir not given")
		# root = pathlib.Path("hardcodedoutplace")
		root = config.general_config.root_directory / label
	else:
		root = pathlib.Path(args.override_root) / label

	if args.skip_to_stage is not None:
		if args.skip_to_stage not in [1, 2, 3, 4]:
			raise ValueError(f"There is no stage {args.skip_to_stage}")
		else:
			skip = kalpaa.config.SkipToStage(args.skip_to_stage - 1)
	else:
		skip = None

	_logger.info(skip)

	overridden_config = dataclasses.replace(
		config,
		general_config=dataclasses.replace(
			config.general_config, root_directory=root.resolve(), skip_to_stage=skip
		),
	)

	kalpaa.common.set_up_logging(
		config,
		log_stream=args.log_stream,
		log_file=str(root / f"logs/kalpaa_{label}.log"),
	)

	completions_status = kalpaa.completions.check_initial_completions(
		args.config_file, overridden_config
	)
	if completions_status == kalpaa.completions.CompletionsStatus.COMPLETE:
		_logger.info("All stages complete, exiting")
		return
	elif completions_status == kalpaa.completions.CompletionsStatus.INVALID:
		_logger.error("Invalid completion status, exiting")
		raise ValueError("Invalid completion status")

	# otherwise good to go

	_logger.info(
		f"Root dir is {root}, copying over {overridden_config.general_config.indexes_json_name}, {overridden_config.general_config.dots_json_name} and {args.config_file}"
	)
	for file in [
		overridden_config.general_config.indexes_json_name,
		overridden_config.general_config.dots_json_name,
		args.config_file,
	]:
		_logger.info(f"Copying {file} to {root}")
		(root / file).write_text((pathlib.Path.cwd() / file).read_text())

	if overridden_config.generation_config.override_measurement_filesets is not None:
		_logger.info(
			f"Overriding measurements with {overridden_config.generation_config.override_measurement_filesets}"
		)
		override_directory = root / kalpaa.config.OVERRIDE_MEASUREMENT_DIR_NAME
		override_directory.mkdir(exist_ok=True, parents=True)
		for (
			key,
			files,
		) in overridden_config.generation_config.override_measurement_filesets.items():
			_logger.info(f"Copying for {key=}, {files} to {override_directory}")
			for file in files:
				fileset_dir = override_directory / key
				fileset_dir.mkdir(exist_ok=True, parents=True)
				_logger.info(f"Copying {file} to {override_directory}")
				(fileset_dir / file).write_text((pathlib.Path.cwd() / file).read_text())

	_logger.info(f"Got {config=}")
	runner = Runner(overridden_config)
	runner.run()


if __name__ == "__main__":
	main()
