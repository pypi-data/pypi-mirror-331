import argparse
import pathlib

import csv
import deepdog
import deepdog.cli.probs
import deepdog.cli.probs.main
import deepdog.direct_monte_carlo.compose_filter
import deepdog.indexify
import deepdog.direct_monte_carlo
import logging

# # import itertools

import kalpaa.stages
import kalpaa.stages.stage03_1
import tantri.cli
import tantri.cli.file_importer
import tantri.dipoles.types

# # from dataclasses import dataclass
#
#
# folder in curr dir
import kalpaa
import kalpaa.common
import kalpaa.completions


_logger = logging.getLogger(__name__)


OUT_FIELDNAMES = [
	"dot_name",
	"target_cost",
	"xmin",
	"xmax",
	"ymin",
	"ymax",
	"zmin",
	"zmax",
	"orientation",
	"avg_filled",
	"log_magnitude",
	"calculations_coalesced",
	"success",
	"count",
	"prob",
]


def coalesced_filename(subdir_name: str) -> str:
	return f"coalesced-{subdir_name}.csv"


def read_coalesced_csv(parent_path: pathlib.Path, subdir_name: str):

	# csv_name = f"coalesced-{dot_name}-{target_cost}.csv"
	csv_path = parent_path / coalesced_filename(subdir_name)
	_logger.debug(f"{csv_path=}")
	with csv_path.open("r", newline="") as csvfile:
		reader = csv.DictReader(csvfile)
		out_list = []

		subdir_split = subdir_name.rsplit("-", 1)

		dot_name = subdir_split[0]
		target_cost = subdir_split[1]
		_logger.debug(f"{dot_name=}, {target_cost=} for subdir_name {subdir_name=}")
		for row in reader:
			row["dot_name"] = dot_name
			row["target_cost"] = target_cost
			out_list.append(row)
		return out_list


class Stage03Runner:
	def __init__(self, config: kalpaa.Config):
		self.config = config
		_logger.info(f"Initialising Stage03 runner with {config=}")

		self.indexifier = self.config.indexifier()

		self.dots = [
			d.label
			for d in tantri.cli.file_importer.read_dots_json_file(
				self.config.absify(self.config.general_config.dots_json_name)
			)
		]
		_logger.info(f"Got dots {self.dots=}")

	def merge_coalesceds(self, sorted_dir: pathlib.Path):
		out_path = sorted_dir / kalpaa.common.merged_coalesced_name()
		with out_path.open("w", newline="") as outfile:
			writer = csv.DictWriter(outfile, OUT_FIELDNAMES)
			writer.writeheader()
			for subdir in sorted_dir.iterdir():
				if not subdir.is_dir():
					_logger.info(f"That's not a dir {subdir=}")
					continue
				subdir_name = subdir.name
				_logger.info(f"Reading for {subdir_name=}")
				rows = read_coalesced_csv(sorted_dir, subdir_name)
				for row in rows:
					writer.writerow(row)

	def run_in_subdir(self, subdir: pathlib.Path):
		"""
		Subdir passed in should be e.g. <>/out/z-10-1/
		"""
		with kalpaa.common.new_cd(subdir):

			_logger.debug(f"Running inside {subdir=}")

			subdir_name = subdir.name
			completion_name = f"stage03_1.job_{subdir_name}.complete"
			completion = kalpaa.completions.check_completion_file(
				self.config, completion_name
			)
			if completion == kalpaa.completions.CompletionsStatus.COMPLETE:
				_logger.info(f"Skipping {completion_name}")
				# continue
			elif completion == kalpaa.completions.CompletionsStatus.INVALID:
				_logger.error(f"Invalid completion status for {completion_name}")
				raise ValueError(f"Invalid completion status for {completion_name}")
			else:
				_logger.info(f"Moving dipoles for {subdir=}")
				kalpaa.stages.stage03_1.move_all_in_dipoles(subdir / "dipoles")
				kalpaa.completions.set_completion_file(self.config, completion_name)

			seed_index = 0

			sorted_dir = pathlib.Path(kalpaa.common.sorted_bayesruns_name())
			_logger.info(f"{sorted_dir.resolve()}")

			for sorted_subdir in sorted_dir.iterdir():
				if not subdir.is_dir():
					_logger.info(f"That's not a dir {subdir=}")
					continue

				seed_index += 1
				# TODO pull out
				# sorted_subdir = sorted_dir / f"{dot}-{cost}"

				# TODO need to refactor deepdog probs method so I don't have to dump into args like this
				probs_args = argparse.Namespace()
				probs_args.bayesrun_directory = sorted_subdir
				probs_args.indexify_json = self.config.absify(
					self.config.general_config.indexes_json_name
				)
				probs_args.coalesced_keys = ""
				probs_args.uncoalesced_outfile = None
				probs_args.coalesced_outfile = sorted_dir / coalesced_filename(
					sorted_subdir.name
				)

				deepdog.cli.probs.main.main(probs_args)

			self.merge_coalesceds(sorted_dir)

	# def run_in_subdir(self, subdir: pathlib.Path):
	#

	def run(self):
		"""Going to iterate over every folder in out_dir, and execute the subdir stuff inside dirs like <kalpa>/out/z-10-2/dipoles"""
		out_dir_path = self.config.get_out_dir_path()
		subdirs = [child for child in out_dir_path.iterdir() if child.is_dir]
		# _logger.info(f"Going to execute within each of the directories in {subdirs=}")
		for subdir in subdirs:
			# skip try finally for now just blow up if problem
			_logger.debug(f"Running for {subdir=}")
			dipoles_dir = subdir / "dipoles"
			dipoles_dir.mkdir(exist_ok=True, parents=False)
			self.run_in_subdir(subdir)


def parse_args():

	parser = argparse.ArgumentParser(
		"Stage03 Runner", formatter_class=argparse.ArgumentDefaultsHelpFormatter
	)

	parser.add_argument(
		"--log-file",
		type=str,
		help="A filename for logging to, if not provided will only log to stderr",
		default=None,
	)
	args = parser.parse_args()
	return args
