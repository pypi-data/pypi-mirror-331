import numpy

import logging

_logger = logging.getLogger(__name__)


def shortest_angular_distance(
	angles_1: numpy.ndarray, angles_2: numpy.ndarray
) -> numpy.ndarray:
	"""
	Compute the shortest angular distance, pairwise, between two sets of angles.
	Assuming that angles in radians, and that the shape of our arrays is what we expect.

	:param angles_1: one array of angles
	:param angles_2: the other array of angles
	:return: array of differences numpy.ndarray
	"""

	result = (angles_1 - angles_2 + numpy.pi) % (2 * numpy.pi) - numpy.pi
	# _logger.debug(f"{angles_1=}")
	# _logger.debug(f"{angles_2=}")
	# _logger.debug(f"{result=}")

	return result
