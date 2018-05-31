# see data.py for more details on the data
from data import LockCData
from combinationlockcracker import CombinationLockCracker
from models import Models


def create_black_and_white_clc(digit_count: int) -> CombinationLockCracker:
	return CombinationLockCracker(digit_count, Models.create_black_and_white_model(digit_count))


def create_difference_distance_clc(digit_count: int) -> CombinationLockCracker:
	return CombinationLockCracker(digit_count, Models.create_distance_model(digit_count))


def create_edit_distance_clc(digit_count: int, encourage_distance: False) -> CombinationLockCracker:
	name = ('edit_cl1_ch1_%ddigits_' % digit_count) + ('encdist' if encourage_distance else 'noencdist')
	return CombinationLockCracker(digit_count, Models.create_distance_model(digit_count, Models.edit_distance,
																			encourage_distance=encourage_distance,
																			model_chosen_name=name))


def print_most_probable(clc: CombinationLockCracker, count: int, adjacency=False, max_distance: int = 2) -> None:
	if adjacency:
		# this takes a bit more time
		mps = clc.most_probable_adjacent(count, max_distance)
	else:
		mps = clc.most_probables(count)
	max_d_string = ("| with max_distance = %d" % max_distance) if adjacency else ""
	print(clc, 'for count =', count, '| adjacency =', adjacency, max_d_string)
	print("\n".join(sorted(["%s: %s" % (str(el), str(round(mps[el], 6))) for el in mps])))


if __name__ == '__main__':
	data_index = 1
	""" using the data index, load the data with either simulated, observed, or random """
	true_combo, digit_count, observations = LockCData.load_observed(data_index)
	# true_combo, digit_count, observations = LockCData.load_simulated(data_index)
	# true_combo, digit_count, observations = LockCData.load_random(data_index)

	""" create a combination lock cracker with one of the models """
	clc = create_black_and_white_clc(digit_count)
	# clc = create_difference_distance_clc(digit_count)
	# clc = create_edit_distance_clc(digit_count, encourage_distance=True)
	# clc = create_edit_distance_clc(digit_count, encourage_distance=False)

	""" train the cracker with the observations given"""
	clc.observe_list(observations)

	""" finally, print the most probable codes after having made the observations """
	print_most_probable(clc, 100, adjacency=False)
	print_most_probable(clc, 100, adjacency=True, max_distance=2)
