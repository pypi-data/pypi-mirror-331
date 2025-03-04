from __future__ import annotations

# useful for measurementgroup which is a type that has itself in method signatures, avoids having to manually specify the typehint as a string

import re
import numpy
import dataclasses
import typing
import json
import pathlib
import logging
import csv
import deepdog.direct_monte_carlo.dmc_filters
import deepdog.direct_monte_carlo.compose_filter
import deepdog.direct_monte_carlo.cost_function_filter
import pdme.util.fast_nonlocal_spectrum

# import tantri.cli

from kalpaa.config import MeasurementTypeEnum
import kalpaa.common.angles

import pdme
import pdme.util.fast_v_calc
import pdme.measurement
import pdme.measurement.input_types

_logger = logging.getLogger(__name__)

X_ELECTRIC_FIELD = "Ex"
POTENTIAL = "V"


def short_string_to_measurement_type(short_string: str) -> MeasurementTypeEnum:
	if short_string == X_ELECTRIC_FIELD:
		return MeasurementTypeEnum.X_ELECTRIC_FIELD
	elif short_string == POTENTIAL:
		return MeasurementTypeEnum.POTENTIAL
	else:
		raise ValueError(f"Could not find {short_string=}")


@dataclasses.dataclass
class Measurement:
	dot_measurement: typing.Optional[pdme.measurement.DotMeasurement]
	stdev: float
	dot_pair_measurement: typing.Optional[pdme.measurement.DotPairMeasurement] = None


@dataclasses.dataclass
class MeasurementGroup:
	_measurements: typing.Sequence[Measurement]
	_measurement_type: MeasurementTypeEnum
	_using_pairs: bool = dataclasses.field(init=False, default=False)

	def validate(self):
		if not self._measurements:
			raise ValueError("Cannot have an empty measurement group")
		using_pairs = any(
			m.dot_pair_measurement is not None for m in self._measurements
		)
		using_singles = any(m.dot_measurement is not None for m in self._measurements)
		if using_pairs and using_singles:
			raise ValueError(
				"Cannot mix single and pair measurements in a single measurement group"
			)
		if not using_pairs and not using_singles:
			raise ValueError("Cannot have a measurement group with no measurements")
		self._using_pairs = using_pairs

	def add(self, other: MeasurementGroup) -> MeasurementGroup:

		if other._measurement_type != self._measurement_type:
			raise ValueError(
				f"Cannot add {other._measurement_type=} to {self._measurement_type=}, as they have different measurement types"
			)

		# this is probably not conformant to the ideal contract for typing.Sequence
		new_measurements = [*self._measurements, *other._measurements]

		return MeasurementGroup(new_measurements, self._measurement_type)

	def _meas_array(self) -> numpy.ndarray:
		if self._using_pairs:
			return numpy.array(
				[
					m.dot_pair_measurement.v
					for m in self._measurements
					if m.dot_pair_measurement is not None
				]
			)
		else:
			return numpy.array(
				[
					m.dot_measurement.v
					for m in self._measurements
					if m.dot_measurement is not None
				]
			)

	def _input_array(self) -> numpy.ndarray:
		if self._using_pairs:
			return pdme.measurement.input_types.dot_pair_inputs_to_array(
				[
					(
						m.dot_pair_measurement.r1,
						m.dot_pair_measurement.r2,
						m.dot_pair_measurement.f,
					)
					for m in self._measurements
					if m.dot_pair_measurement is not None
				]
			)
		else:
			return pdme.measurement.input_types.dot_inputs_to_array(
				[
					(m.dot_measurement.r, m.dot_measurement.f)
					for m in self._measurements
					if m.dot_measurement is not None
				]
			)

	def _stdev_array(self) -> numpy.ndarray:
		return numpy.array([m.stdev for m in self._measurements])

	def cost_function(self):
		self.validate()
		meas_array = self._meas_array()

		_logger.debug(f"Obtained {meas_array=}")

		input_array = self._input_array()
		_logger.debug(f"Obtained {input_array=}")

		return CostFunction(self._measurement_type, input_array, meas_array)

	def stdev_cost_function(
		self,
		use_log_noise: bool = False,
	):
		self.validate()
		stdev_array = self._stdev_array()

		meas_array = self._meas_array()

		_logger.debug(f"Obtained {meas_array=}")

		input_array = self._input_array()
		_logger.debug(f"Obtained {input_array=}")

		return StDevUsingCostFunction(
			self._measurement_type,
			input_array,
			meas_array,
			stdev_array,
			log_noise=use_log_noise and not self._using_pairs,
			use_pair_measurement=self._using_pairs,
		)


class CostFunction:
	def __init__(
		self,
		measurement_type: MeasurementTypeEnum,
		dot_inputs_array: numpy.ndarray,
		actual_measurement_array: numpy.ndarray,
		use_pair_measurement: bool = False,
	):
		"""
		Construct a cost function that uses the measurements.

		:param measurement_type: The type of measurement we're using.
		:param dot_inputs_array: The array of dot inputs.
		:param actual_measurement_array: The actual measurements.
		:param use_pair_measurement: Whether to use pair measurements. (default false)
		"""
		_logger.info(f"Cost function with measurement type of {measurement_type}")
		self.measurement_type = measurement_type
		self.dot_inputs_array = dot_inputs_array
		self.actual_measurement_array = actual_measurement_array
		self.actual_measurement_array2 = actual_measurement_array**2
		self.use_pair_measurement = use_pair_measurement
		if self.use_pair_measurement:
			raise NotImplementedError("Pair measurements are not yet supported")

	def __call__(self, dipoles_to_test):
		if self.measurement_type == MeasurementTypeEnum.X_ELECTRIC_FIELD:
			vals = pdme.util.fast_v_calc.fast_efieldxs_for_dipoleses(
				self.dot_inputs_array, dipoles_to_test
			)
		elif self.measurement_type == MeasurementTypeEnum.POTENTIAL:
			vals = pdme.util.fast_v_calc.fast_vs_for_dipoleses(
				self.dot_inputs_array, dipoles_to_test
			)
		diffs = (
			vals - self.actual_measurement_array
		) ** 2 / self.actual_measurement_array2
		return numpy.sqrt(diffs.mean(axis=-1))


class StDevUsingCostFunction:
	def __init__(
		self,
		measurement_type: MeasurementTypeEnum,
		dot_inputs_array: numpy.ndarray,
		actual_measurement_array: numpy.ndarray,
		actual_stdev_array: numpy.ndarray,
		log_noise: bool = False,
		use_pair_measurement: bool = False,
	):
		"""
		Construct a cost function that uses the standard deviation of the measurements.

		:param measurement_type: The type of measurement we're using.
		:param dot_inputs_array: The array of dot inputs. (may be actually inputses for pair measurements)
		:param actual_measurement_array: The actual measurements.
		:param actual_stdev_array: The actual standard deviations.
		:param use_pair_measurement: Whether to use pair measurements. (default false)
		:param log_noise: Whether to use log noise. (default false but we should probably use it)
		"""
		_logger.info(f"Cost function with measurement type of {measurement_type}")
		self.measurement_type = measurement_type
		self.dot_inputs_array = dot_inputs_array
		self.actual_measurement_array = actual_measurement_array
		self.actual_measurement_array2 = actual_measurement_array**2
		self.actual_stdev_array = actual_stdev_array
		self.actual_stdev_array2 = actual_stdev_array**2

		self.use_log_noise = log_noise
		self.log_actual = numpy.log(self.actual_measurement_array)
		self.log_denom2 = (
			numpy.log(self.actual_stdev_array + self.actual_measurement_array)
			- numpy.log(self.actual_measurement_array)
		) ** 2
		self.use_pair_measurement = use_pair_measurement

	def __call__(self, dipoles_to_test):
		if self.use_pair_measurement:
			# We're going to just use phase data, rather than correlation data for now.
			# We'll probably need to do some re-architecting later to get the phase vs correlation flag to propagate here
			# if self.use_log_noise:
			# 	_logger.info("No log noise for phase data, which is wrapped but linear")

			if self.measurement_type == MeasurementTypeEnum.X_ELECTRIC_FIELD:
				vals = pdme.util.fast_nonlocal_spectrum.fast_s_spin_qubit_tarucha_nonlocal_dipoleses(
					self.dot_inputs_array, dipoles_to_test
				)
			elif self.measurement_type == MeasurementTypeEnum.POTENTIAL:
				vals = pdme.util.fast_nonlocal_spectrum.fast_s_nonlocal_dipoleses(
					self.dot_inputs_array, dipoles_to_test
				)

			# _logger.debug(f"Got {vals=}")

			sign_vals = pdme.util.fast_nonlocal_spectrum.signarg(vals)

			# _logger.debug(f"Got {sign_vals=}")
			diffs = (
				kalpaa.common.angles.shortest_angular_distance(
					sign_vals, self.actual_measurement_array
				)
				** 2
			)
			# _logger.debug(f"Got {diffs=}")
			scaled_diffs = diffs / self.actual_stdev_array2
			# _logger.debug(f"Got {scaled_diffs=}")
			return numpy.sqrt(scaled_diffs.mean(axis=-1))

		else:
			if self.measurement_type == MeasurementTypeEnum.X_ELECTRIC_FIELD:
				vals = pdme.util.fast_v_calc.fast_efieldxs_for_dipoleses(
					self.dot_inputs_array, dipoles_to_test
				)
			elif self.measurement_type == MeasurementTypeEnum.POTENTIAL:
				vals = pdme.util.fast_v_calc.fast_vs_for_dipoleses(
					self.dot_inputs_array, dipoles_to_test
				)

			if self.use_log_noise:
				diffs = ((numpy.log(vals) - self.log_actual) ** 2) / self.log_denom2
			else:
				diffs = (
					(vals - self.actual_measurement_array) ** 2
				) / self.actual_stdev_array2

			return numpy.sqrt(diffs.mean(axis=-1))


# the key for frequencies in what we return
RETURNED_FREQUENCIES_KEY = "frequencies"


def read_dots_json(json_file: pathlib.Path) -> typing.Dict:
	try:
		with open(json_file, "r") as file:
			return _reshape_dots_dict(json.load(file))
	except Exception as e:
		_logger.error(
			f"Had a bad time reading the dots file {json_file}, sorry.", exc_info=e
		)
		raise e


def _reshape_dots_dict(dots_dict: typing.Sequence[typing.Dict]) -> typing.Dict:
	ret = {}
	for dot in dots_dict:
		ret[dot["label"]] = dot["r"]
	return ret


BINNED_HEADER_REGEX = r"\s*APSD_(?P<measurement_type>\w+)_(?P<dot_name>\w+)_(?P<summary_stat>mean|stdev)\s*"
PAIR_MEASUREMENT_BINNED_HEADER_REGEX = r"\s*CPSD_(?P<cpsd_type>correlation|phase)_(?P<measurement_type>\w+)_(?P<dot_name>\w+)_(?P<dot_name2>\w+)_(?P<summary_stat>mean|stdev)\s*"


@dataclasses.dataclass
class ParsedBinHeader:
	original_field: str
	measurement_type: MeasurementTypeEnum
	summary_stat: str
	dot_name: str
	# only used for pair measurements
	dot_name2: typing.Optional[str] = None
	cpsd_type: typing.Optional[typing.Literal["correlation", "phase"]] = None

	@property
	def pair(self) -> bool:
		return self.dot_name2 is not None


def _parse_bin_header(field: str) -> typing.Optional[ParsedBinHeader]:
	"""
	Parse a binned header field into a ParsedBinHeader object.

	Return None if the field does not match the expected format (and thus no match).
	"""
	if (match := re.match(BINNED_HEADER_REGEX, field)) is not None:
		match_groups = match.groupdict()
		return ParsedBinHeader(
			original_field=field,
			measurement_type=short_string_to_measurement_type(
				match_groups["measurement_type"]
			),
			dot_name=match_groups["dot_name"],
			summary_stat=match_groups["summary_stat"],
		)
	elif (
		pair_match := re.match(PAIR_MEASUREMENT_BINNED_HEADER_REGEX, field)
	) is not None:
		groups = pair_match.groupdict()
		cpsd_type = typing.cast(
			typing.Literal["correlation", "phase"], groups["cpsd_type"]
		)
		return ParsedBinHeader(
			original_field=field,
			measurement_type=short_string_to_measurement_type(
				groups["measurement_type"]
			),
			dot_name=groups["dot_name"],
			dot_name2=groups["dot_name2"],
			cpsd_type=cpsd_type,
			summary_stat=groups["summary_stat"],
		)
	else:
		_logger.debug(f"Could not parse {field=}")
		return None


@dataclasses.dataclass
class CSV_BinnedData:
	measurement_type: MeasurementTypeEnum
	single_dot_dict: typing.Dict[str, typing.Any]
	pair_dot_dict: typing.Dict[typing.Tuple[str, str], typing.Any]
	freqs: typing.Sequence[float]


def read_bin_csv(
	csv_file: pathlib.Path,
) -> CSV_BinnedData:
	"""
	Read a binned csv file and return the measurement type and the binned data.

	:param csv_file: The csv file to read.
	:return: A tuple of the measurement type and the binned data.
	"""

	measurement_type = None
	_logger.info(f"Assuming measurement type is {measurement_type} for now")
	try:
		with open(csv_file, "r", newline="") as file:
			reader = csv.DictReader(file)
			fields = reader.fieldnames

			if fields is None:
				raise ValueError(
					f"Really wanted our fields for file {file=} to be non-None, but they're None"
				)
			freq_field = fields[0]

			remaining_fields = fields[1:]
			_logger.debug(f"Going to read frequencies from {freq_field=}")

			parsed_headers = {}
			freq_list = []
			aggregated_dict: typing.Dict[str, typing.Any] = {
				RETURNED_FREQUENCIES_KEY: []
			}
			pair_aggregated_dict: typing.Dict[typing.Tuple[str, str], typing.Any] = {}

			for field in remaining_fields:
				parsed_header = _parse_bin_header(field)
				if parsed_header is None:
					_logger.warning(f"Could not parse {field=}")
					continue
				parsed_headers[field] = parsed_header

				# Get our dictionary structures set up by initialising empty dictionaries for each new field as we go
				if parsed_header.pair:
					if parsed_header.dot_name2 is None:
						raise ValueError(
							f"Pair measurement {field=} has no dot_name2, but it should"
						)
					dot_names = (parsed_header.dot_name, parsed_header.dot_name2)
					if dot_names not in pair_aggregated_dict:
						pair_aggregated_dict[dot_names] = {}

					if (
						parsed_header.summary_stat
						not in pair_aggregated_dict[dot_names]
					):
						pair_aggregated_dict[dot_names][parsed_header.summary_stat] = []

				else:
					if parsed_header.dot_name not in aggregated_dict:
						aggregated_dict[parsed_header.dot_name] = {}

					if (
						parsed_header.summary_stat
						not in aggregated_dict[parsed_header.dot_name]
					):
						aggregated_dict[parsed_header.dot_name][
							parsed_header.summary_stat
						] = []

				# Realistically we'll always have the same measurement type, but this warning may help us catch out cases where this didn't happen correctly
				# We should only need to set it once, so the fact we keep checking is more about catching errors than anything else
				if measurement_type is not None:
					if measurement_type != parsed_header.measurement_type:
						_logger.warning(
							f"Attempted to set already set measurement type {measurement_type}. Allowing the switch to {parsed_header.measurement_type}, but it's problematic"
						)
				measurement_type = parsed_header.measurement_type

			_logger.debug("finished parsing headers")
			_logger.debug("throwing away the measurement type for now")

			for row in reader:
				# _logger.debug(f"Got {row=}")
				freq_list.append(float(row[freq_field].strip()))
				# don't need to set, but keep for legacy
				aggregated_dict[RETURNED_FREQUENCIES_KEY].append(
					float(row[freq_field].strip())
				)
				for field, parsed_header in parsed_headers.items():
					if parsed_header.pair:
						if parsed_header.dot_name2 is None:
							raise ValueError(
								f"Pair measurement {field=} has no dot_name2, but it should"
							)
						value = float(row[field].strip())
						dot_names = (parsed_header.dot_name, parsed_header.dot_name2)
						pair_aggregated_dict[dot_names][
							parsed_header.summary_stat
						].append(value)
					else:
						value = float(row[field].strip())
						aggregated_dict[parsed_header.dot_name][
							parsed_header.summary_stat
						].append(value)

			if measurement_type is None:
				raise ValueError(
					f"For some reason {measurement_type=} is None? We want to know our measurement type."
				)

			return CSV_BinnedData(
				measurement_type=measurement_type,
				single_dot_dict=aggregated_dict,
				freqs=freq_list,
				pair_dot_dict=pair_aggregated_dict,
			)
	except Exception as e:
		_logger.error(
			f"Had a bad time reading the binned data {csv_file}, sorry.", exc_info=e
		)
		raise e


@dataclasses.dataclass
class BinnedData:
	dots_dict: typing.Dict
	csv_dict: typing.Dict[str, typing.Any]
	measurement_type: MeasurementTypeEnum
	pair_dict: typing.Dict[typing.Tuple[str, str], typing.Any]
	freq_list: typing.Sequence[float]

	# we're ignoring stdevs for the current moment, as in the calculator single_dipole_matches.py script.
	def _dot_to_measurements(self, dot_name: str) -> MeasurementGroup:
		if dot_name not in self.dots_dict:
			raise KeyError(f"Could not find {dot_name=} in {self.dots_dict=}")
		if dot_name not in self.csv_dict:
			raise KeyError(f"Could not find {dot_name=} in {self.csv_dict=}")

		dot_r = self.dots_dict[dot_name]
		freqs = self.freq_list
		vs = self.csv_dict[dot_name]["mean"]
		stdevs = self.csv_dict[dot_name]["stdev"]

		return MeasurementGroup(
			[
				Measurement(
					dot_measurement=pdme.measurement.DotMeasurement(f=f, v=v, r=dot_r),
					stdev=stdev,
				)
				for f, v, stdev in zip(freqs, vs, stdevs)
			],
			_measurement_type=self.measurement_type,
		)

	def _dot_to_stdev(self, dot_name: str) -> typing.Sequence[float]:
		if dot_name not in self.dots_dict:
			raise KeyError(f"Could not find {dot_name=} in {self.dots_dict=}")
		if dot_name not in self.csv_dict:
			raise KeyError(f"Could not find {dot_name=} in {self.csv_dict=}")

		stdevs = self.csv_dict[dot_name]["stdev"]

		return stdevs

	def _pair_to_measurements(
		self, dot_pair_name: typing.Tuple[str, str]
	) -> MeasurementGroup:
		if dot_pair_name not in self.pair_dict:
			raise KeyError(f"Could not find {dot_pair_name=} in {self.pair_dict=}")

		dot_name1, dot_name2 = dot_pair_name
		if dot_name1 not in self.dots_dict:
			raise KeyError(f"Could not find {dot_name1=} in {self.dots_dict=}")
		if dot_name2 not in self.dots_dict:
			raise KeyError(f"Could not find {dot_name2=} in {self.dots_dict=}")

		dot_r1 = self.dots_dict[dot_name1]
		dot_r2 = self.dots_dict[dot_name2]
		freqs = self.freq_list
		vs = self.pair_dict[dot_pair_name]["mean"]
		stdevs = self.pair_dict[dot_pair_name]["stdev"]

		return MeasurementGroup(
			[
				Measurement(
					dot_measurement=None,
					dot_pair_measurement=pdme.measurement.DotPairMeasurement(
						f=f, v=v, r1=dot_r1, r2=dot_r2
					),
					stdev=stdev,
				)
				for f, v, stdev in zip(freqs, vs, stdevs)
			],
			_measurement_type=self.measurement_type,
		)

	def measurements(self, dot_names: typing.Sequence[str]) -> MeasurementGroup:
		_logger.debug(f"Constructing measurements for dots {dot_names=}")
		ret = MeasurementGroup([], self.measurement_type)
		_logger.debug
		for dot_name in dot_names:
			ret = ret.add(self._dot_to_measurements(dot_name))
		return ret

	def pair_measurements(
		self, dot_pair_names: typing.Sequence[typing.Tuple[str, str]]
	) -> MeasurementGroup:
		_logger.debug(f"Constructing measurements for dot pairs {dot_pair_names=}")
		ret = MeasurementGroup([], self.measurement_type)
		_logger.debug
		for dot_pair_name in dot_pair_names:
			ret = ret.add(self._pair_to_measurements(dot_pair_name))
		return ret

	# def _cost_function(self, mg: MeasurementGroup):
	# 	meas_array = mg.meas_array()

	# 	_logger.debug(f"Obtained {meas_array=}")

	# 	input_array = mg.input_array()
	# 	_logger.debug(f"Obtained {input_array=}")

	# 	return CostFunction(self.measurement_type, input_array, meas_array)

	# def _stdev_cost_function(
	# 	self,
	# 	mg: MeasurementGroup,
	# 	use_log_noise: bool = False,
	# ):
	# 	stdev_array = mg.stdev_array()

	# 	meas_array = mg.meas_array()

	# 	_logger.debug(f"Obtained {meas_array=}")

	# 	input_array = mg.input_array()
	# 	_logger.debug(f"Obtained {input_array=}")

	# 	return StDevUsingCostFunction(
	# 		self.measurement_type,
	# 		input_array,
	# 		meas_array,
	# 		stdev_array,
	# 		log_noise=use_log_noise,
	# 	)

	def _get_measurement_from_dot_name_or_pair(
		self,
		dot_names_or_pairs: typing.Union[
			typing.Sequence[str], typing.Sequence[typing.Tuple[str, str]]
		],
	) -> MeasurementGroup:
		"""
		check if dot_names_or_pairs is a list of strings or a list of tuples of strings, then return the appropriate measurement group
		"""
		if isinstance(dot_names_or_pairs[0], str):
			_logger.debug("first item was a string, assuming we're specifying strings")
			# we expect all strings, fail if otherwise
			names = []
			for dn in dot_names_or_pairs:
				if not isinstance(dn, str):
					raise ValueError(f"Expected all strings in {dot_names_or_pairs=}")
				names.append(dn)
			_logger.debug(f"Constructing measurements for dots {names=}")
			return self.measurements(names)
		else:
			_logger.debug("trying out pairs")
			pairs = []
			for dn in dot_names_or_pairs:
				if not isinstance(dn, tuple):
					raise ValueError(f"Expected all tuples in {dot_names_or_pairs=}")
				pairs.append(dn)
			_logger.debug(f"Constructing measurements for dot pairs {pairs=}")
			return self.pair_measurements(pairs)

	def cost_function_filter(
		self,
		dot_names_or_pairs: typing.Union[
			typing.Sequence[str], typing.Sequence[typing.Tuple[str, str]]
		],
		target_cost: float,
	):
		measurements = self._get_measurement_from_dot_name_or_pair(dot_names_or_pairs)
		cost_function = measurements.cost_function()
		return deepdog.direct_monte_carlo.cost_function_filter.CostFunctionTargetFilter(
			cost_function, target_cost
		)

	def stdev_cost_function_filter(
		self,
		dot_names_or_pairs: typing.Union[
			typing.Sequence[str], typing.Sequence[typing.Tuple[str, str]]
		],
		target_cost: float,
		use_log_noise: bool = False,
	):
		measurements = self._get_measurement_from_dot_name_or_pair(dot_names_or_pairs)
		cost_function = measurements.stdev_cost_function(use_log_noise=use_log_noise)
		return deepdog.direct_monte_carlo.cost_function_filter.CostFunctionTargetFilter(
			cost_function, target_cost
		)


def read_dots_and_binned(json_file: pathlib.Path, csv_file: pathlib.Path) -> BinnedData:
	dots = read_dots_json(json_file)
	csv_data = read_bin_csv(csv_file)
	return BinnedData(
		measurement_type=csv_data.measurement_type,
		dots_dict=dots,
		csv_dict=csv_data.single_dot_dict,
		freq_list=csv_data.freqs,
		pair_dict=csv_data.pair_dot_dict,
	)
