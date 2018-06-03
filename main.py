# see data.py for more details on the data
from data import LockCData
from combinationlockcracker import CombinationLockCracker
from models import Models


def create_black_and_white_clc(digit_count: int) -> CombinationLockCracker:
	""" create a b&w combination lock cracker for digit count """
	return CombinationLockCracker(digit_count, Models.create_black_and_white_model(digit_count))


def create_difference_distance_clc(digit_count: int) -> CombinationLockCracker:
	""" create a DDM combination lock cracker for digit count """
	return CombinationLockCracker(digit_count, Models.create_distance_model(digit_count))


def create_edit_distance_clc(digit_count: int, encourage_distance: bool = False) -> CombinationLockCracker:
	""" create an EDM combination lock cracker for digit count """
	# the naming convention here describes how the edit distance
	# function behaves. See Models.edit_distance for details
	name = ('edit_cl1_ch1_%ddigits_' % digit_count) + ('encdist' if encourage_distance else 'noencdist')
	d_model = Models.create_distance_model(digit_count, Models.edit_distance, model_name=name,
										   enc_dist=encourage_distance, is_edit_distance=True)
	return CombinationLockCracker(digit_count, d_model)


def create_edit_distance_one_direction_clc(digit_count: int, encourage_distance: bool = False,
										  up: bool = True) -> CombinationLockCracker:
	up_text = 'up' if up else 'down'
	name = ('edit_%s_cl1_ch1_%ddigits_' % (up_text, digit_count)) + ('encdist' if encourage_distance else 'noencdist')
	replace_cost_func = Models.replace_cost_by_rotations_up if up else Models.replace_cost_by_rotations_down
	distance_func = lambda obs, act, d_count: Models.edit_distance(obs, act, d_count, replace_cost_func)
	d_model = Models.create_distance_model(digit_count, distance_func, model_name=name,
										   enc_dist=encourage_distance, is_edit_distance=True)
	return CombinationLockCracker(digit_count, d_model)


def print_most_probable(clc: CombinationLockCracker, count: int, adjacency=False, max_distance: int = 2) -> None:
	""" after having done all the observations, print the result"""
	if adjacency:
		# this takes quite a lot of time if max_distance is > 3
		mps = clc.most_probable_adjacent(count, max_distance)
	else:
		mps = clc.most_probables(count)
	max_d_string = ("| with max_distance = %d" % max_distance) if adjacency else ""
	print(clc, 'for count =', count, '| adjacency =', adjacency, max_d_string)
	print("\n".join(sorted(["%s: %s" % (str(el), str(round(mps[el], 10))) for el in mps])))


if __name__ == '__main__':
	data_set_type, data_index = 1,1
	data_name = ["observed_%d.txt", "simulated_%d.txt", "random_%d.txt"]
	""" using the data index, load the data with either simulated, observed, or random """
	print("\n* " +(data_name[data_set_type - 1] % data_index) + " * \n")
	if data_set_type == 1:
		true_combo, digit_count, observations = LockCData.load_observed(data_index)
	elif data_set_type == 2:
		true_combo, digit_count, observations = LockCData.load_simulated(data_index)
	elif data_set_type == 3:
		true_combo, digit_count, observations = LockCData.load_random(data_index)
	else:
		raise Exception('invalid data type')

	""" create a combination lock cracker with one of the models """
	clc = create_black_and_white_clc(digit_count)
	# clc = create_difference_distance_clc(digit_count)
	# clc = create_edit_distance_clc(digit_count, encourage_distance=False)
	# clc = create_edit_distance_clc(digit_count, encourage_distance=True)
	# clc = create_edit_distance_one_direction_clc(digit_count, encourage_distance=False, up=True)
	# clc = create_edit_distance_one_direction_clc(digit_count, encourage_distance=False, up=False)

	""" train the cracker with the observations given"""
	clc.observe_list(observations)

	""" finally, print the most probable codes after having made the observations """
	print_most_probable(clc, 100, adjacency=False)
	for k in range(2, 4):
		print('max_distance = %d' % k)
		print_most_probable(clc, 100, adjacency=True, max_distance=k)