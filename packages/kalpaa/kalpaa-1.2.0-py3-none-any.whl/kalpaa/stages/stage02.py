import argparse
import pathlib

# import csv
import deepdog
import deepdog.direct_monte_carlo.compose_filter
import deepdog.indexify
import deepdog.direct_monte_carlo
import logging

import tantri.cli
import tantri.cli.file_importer
import tantri.dipoles.types
import typing

import json

import kalpaa
import kalpaa.common
import kalpaa.completions


_logger = logging.getLogger(__name__)

# LOG_PATTERN = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s"


# JOBS = list(range(18))
# TOOD move to json file and read
# COSTS = [10.0, 5.0, 1.0, 0.5, 0.1, 0.06]
# DOTS_DICT = {
# 	"dot1": "dot1",
# 	"dot2": "dot1,dot2",
# 	"line": "dot1,dot2,line",
# 	"triangle1": "dot1,dot2,triangle1",
# 	"triangle2": "dot1,dot2,triangle2",
# 	"uprise1": "dot1,dot2,uprise1",
# 	"uprise2": "dot1,dot2,uprise2",
# }


def enumify_orientation_string(
	orientation_string: str,
) -> tantri.dipoles.types.Orientation:
	canonical_orientation_string = orientation_string.upper()

	if canonical_orientation_string in ["FIXEDZ", "Z"]:
		return tantri.dipoles.types.Orientation.Z

	if canonical_orientation_string in ["FIXEDXY", "XY"]:
		return tantri.dipoles.types.Orientation.XY

	if canonical_orientation_string in ["FREE", "RANDOM"]:
		return tantri.dipoles.types.Orientation.RANDOM

	else:
		raise ValueError(
			f"Could not find match for orientation_string {orientation_string=}"
		)


class Stage02Runner:
	def __init__(self, config: kalpaa.Config):
		self.config = config
		_logger.info(f"Initialising Stage02 runner with {config=}")

		with config.absify(config.general_config.indexes_json_name).open(
			"r"
		) as indexify_json_file:
			indexify_spec = json.load(indexify_json_file)
			indexify_data = indexify_spec["indexes"]
			if "seed_spec" in indexify_spec:
				seed_spec = indexify_spec["seed_spec"]
				indexify_data[seed_spec["field_name"]] = list(
					range(seed_spec["num_seeds"])
				)

			_logger.info(f"loading indexifier with data {indexify_data=}")
			self.indexifier = deepdog.indexify.Indexifier(indexify_data)

		self.dots = tantri.cli.file_importer.read_dots_json_file(
			self.config.absify(self.config.general_config.dots_json_name)
		)
		_logger.info(f"Got dots {self.dots=}")

	def _dots_to_include(self, current_dot: str) -> typing.List[str]:
		if current_dot == "dot1":
			return ["dot1"]
		if current_dot == "dot2":
			return ["dot1", "dot2"]
		else:
			return ["dot1", "dot2", current_dot]

	def run_in_subdir(
		self, subdir: pathlib.Path, override_key: typing.Optional[str] = None
	):
		with kalpaa.common.new_cd(subdir):
			_logger.debug(f"Running inside {subdir=}")

			# TODO hardcoding that we're executing every job index.
			num_jobs = len(self.indexifier)
			_logger.debug(f"Have {num_jobs=}")
			seed_index = 0
			for job_index in range(num_jobs):

				_logger.debug(f"Working on {job_index=}")
				completion_name = f"stage02.job_{job_index}.complete"
				completion = kalpaa.completions.check_completion_file(
					self.config, completion_name
				)
				if completion == kalpaa.completions.CompletionsStatus.COMPLETE:
					_logger.info(f"Skipping {completion_name}")
					continue
				elif completion == kalpaa.completions.CompletionsStatus.INVALID:
					_logger.error(f"Invalid completion status for {completion_name}")
					raise ValueError(f"Invalid completion status for {completion_name}")

				for cost in self.config.deepdog_config.costs_to_try:
					if self.config.deepdog_config.manual_dot_seeds is not None:
						for config_i, manual_config in enumerate(
							self.config.deepdog_config.manual_dot_seeds
						):

							seed_index += 1
							# validate config

							dot_label = str(config_i) + str(manual_config).translate(
								str.maketrans("", "", "[]\",' ")
							)
							dot_set = set()
							for dot_entry in manual_config:
								for dot_name in dot_entry:
									dot_set.add(dot_name)
							_logger.info(f"Dot set {dot_set=}")
							dot_included = ",".join([d for d in sorted(dot_set)])
							trial_name = (
								f"{dot_label}-{dot_included}-{cost}-{job_index}"
							)

							_logger.info(f"Working on {trial_name=}")
							_logger.debug(f"Have {seed_index=}")
							self.single_run_in_subdir(
								job_index,
								cost,
								dot_label,
								trial_name,
								seed_index,
								override_name=override_key,
								dot_spec=manual_config,
							)
					else:
						for dot in self.dots:

							seed_index += 1

							combined_dot_name = ",".join(
								[d for d in self._dots_to_include(dot.label)]
							)
							trial_name = (
								f"{dot.label}-{combined_dot_name}-{cost}-{job_index}"
							)

							_logger.info(f"Working on {trial_name=}")
							_logger.debug(f"Have {seed_index=}")
							self.single_run_in_subdir(
								job_index,
								cost,
								dot.label,
								trial_name,
								seed_index,
								override_name=override_key,
							)
				kalpaa.completions.set_completion_file(self.config, completion_name)

	def single_run_in_subdir(
		self,
		job_index: int,
		cost: float,
		dot_name: str,
		trial_name: str,
		seed_index: int,
		override_name: typing.Optional[str] = None,
		dot_spec: typing.Optional[typing.Sequence[typing.Sequence[str]]] = None,
	):
		# _logger.info(f"Got job index {job_index}")
		# NOTE This guy runs inside subdirs, obviously. In something like <kalpa>/out/z-10-2/dipoles

		# we had job_index, trial_name, args let's see what we need

		_logger.debug(
			f"run_analysis() being called with ({job_index=}, {cost=}, {dot_name=}, {trial_name=}, {seed_index=})"
		)

		_logger.info(
			f"Have {self.config.generation_config.tantri_configs} as our tantri_configs"
		)
		num_tantri_configs = len(self.config.generation_config.tantri_configs)

		if override_name is not None:
			if self.config.generation_config.override_measurement_filesets is None:
				raise ValueError(
					"override_name provided but no override_measurement_filesets, shouldn't be possible to get here"
				)
			_logger.info(f"Time to read override measurement fileset {override_name}")
			override_dir = self.config.get_override_dir_path() / override_name
			override_measurements = (
				self.config.generation_config.override_measurement_filesets[
					override_name
				]
			)
			_logger.info(f"Finding files {override_measurements} in {override_dir}")
			binned_datas = [
				kalpaa.read_dots_and_binned(
					self.config.get_dots_json_path(),
					override_dir / measurement,
				)
				for measurement in override_measurements
			]
		else:

			binned_datas = [
				kalpaa.read_dots_and_binned(
					self.config.get_dots_json_path(),
					pathlib.Path("..")
					/ kalpaa.common.tantri_binned_output_name(tantri_index),
				)
				for tantri_index in range(num_tantri_configs)
			]

		single_dot_names: typing.List[str] = []
		pair_dot_names: typing.List[typing.Tuple[str, str]] = []
		if dot_spec is not None:
			_logger.info(f"Received dot_spec {dot_spec}, validating")
			for dot_entry in dot_spec:
				_logger.debug(f"Working on {dot_entry=}")
				if len(dot_entry) not in (1, 2):
					raise ValueError(
						f"Invalid dot spec {dot_spec}, {dot_entry} has wrong length"
					)

				if len(dot_entry) == 1:
					_logger.debug(f"Adding {dot_entry[0]} to single_dot_names")
					single_dot_names.append(dot_entry[0])
				else:
					pair_dot_names.append((dot_entry[0], dot_entry[1]))
		else:
			single_dot_names = self._dots_to_include(dot_name)
			pair_dot_names = []
		_logger.debug(f"Got dot names {single_dot_names=}, {pair_dot_names=}")

		models = []

		indexes = self.indexifier.indexify(job_index)

		_logger.debug(f"indexes are {indexes}")

		log_magnitude = indexes["magnitudes"]
		avg_filled = indexes["occupancies"]
		orientation = enumify_orientation_string(indexes["orientations"])
		# we are just finding matches given a single seed so don't need to change this
		seed = seed_index

		# TODO find way to store this as a global config file
		# TODO refactor to account for missing entries, (ex. if occupancy of 150 should use next highest value)
		occupancies_dict = {
			1: (500, 1000),
			2: (250, 2000),
			3: (250, 2000),
			5: (100, 5000),
			10: (50, 10000),
			16: (50, 10000),
			17: (50, 10000),
			31: (50, 10000),
			56: (25, 20000),
			100: (2, 250000),
			161: (1, 500000),
			200: (1, 500000),
		}

		mccount, mccountcycles = occupancies_dict[avg_filled]

		model_params = self.config.default_model_param_config.reduced_model_params(
			count=avg_filled, log_magnitude=log_magnitude, orientation=orientation
		)

		models.append(kalpaa.get_model(model_params))

		_logger.info(f"have {len(models)} models to look at")
		if len(models) == 1:
			_logger.info(f"only one model, name: {models[0][0]}")

		deepdog_config = deepdog.direct_monte_carlo.DirectMonteCarloConfig(
			monte_carlo_count_per_cycle=mccount,
			monte_carlo_cycles=mccountcycles,
			target_success=self.config.deepdog_config.target_success,
			max_monte_carlo_cycles_steps=self.config.deepdog_config.max_monte_carlo_cycles_steps,
			monte_carlo_seed=seed,
			write_successes_to_file=True,
			tag=trial_name,
			write_bayesrun_file=True,
			bayesrun_file_timestamp=False,
			skip_if_exists=True,  # Can't see why we wouldn't want this, maybe hook to check_completions later
		)

		_logger.info(f"{deepdog_config=}")

		stdev_cost_function_filters = []

		if len(pair_dot_names):
			pair_stdev_cost_function_filters = [
				b.stdev_cost_function_filter(
					pair_dot_names, cost, self.config.deepdog_config.use_log_noise
				)
				for b in binned_datas
			]
			stdev_cost_function_filters.extend(pair_stdev_cost_function_filters)

		if len(single_dot_names):
			single_stdev_cost_function_filters = [
				b.stdev_cost_function_filter(
					single_dot_names, cost, self.config.deepdog_config.use_log_noise
				)
				for b in binned_datas
			]
			stdev_cost_function_filters.extend(single_stdev_cost_function_filters)

		_logger.debug(f"{stdev_cost_function_filters=}")
		combining_filter = deepdog.direct_monte_carlo.compose_filter.ComposedDMCFilter(
			stdev_cost_function_filters
		)

		run = deepdog.direct_monte_carlo.DirectMonteCarloRun(
			model_name_pairs=models,
			filter=combining_filter,
			config=deepdog_config,
		)
		results = run.execute()
		_logger.info(results)

	def run(self):
		if self.config.generation_config.override_measurement_filesets is not None:
			_logger.info("Using override configuration.")
			for (
				override_name
			) in self.config.generation_config.override_measurement_filesets.keys():
				subdir = self.config.get_out_dir_path() / override_name
				dipoles_dir = subdir / "dipoles"
				dipoles_dir.mkdir(exist_ok=True, parents=False)
				self.run_in_subdir(dipoles_dir, override_key=override_name)

		else:
			"""Going to iterate over every folder in out_dir, and execute the subdir stuff inside dirs like <kalpa>/out/z-10-2/dipoles"""
			out_dir_path = self.config.get_out_dir_path()
			subdirs = [child for child in out_dir_path.iterdir() if child.is_dir]
			# _logger.info(f"Going to execute within each of the directories in {subdirs=}")
			for subdir in subdirs:
				# skip try finally for now just blow up if problem
				_logger.debug(f"Running for {subdir=}")
				dipoles_dir = subdir / "dipoles"
				dipoles_dir.mkdir(exist_ok=True, parents=False)
				self.run_in_subdir(subdir / "dipoles")


def parse_args():

	parser = argparse.ArgumentParser(
		"Stage02 Runner", formatter_class=argparse.ArgumentDefaultsHelpFormatter
	)

	parser.add_argument(
		"--log-file",
		type=str,
		help="A filename for logging to, if not provided will only log to stderr",
		default=None,
	)
	args = parser.parse_args()
	return args
