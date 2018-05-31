# use pickle to store models that are created because
# it can take quite a while to create some of them
import pickle
import utils
from distribution import Distribution
from typing import Callable


class Models:
	@staticmethod
	def create_black_and_white_model(digit_count: int) -> Callable:
		"""
		the black and white model is a model such that the probability of
		observing O given that that the true value is A is 1/10^digit_count i
		f O equals A else 1 minus that.

		Intuition:
			This model is based on the intuition that whenever someone locks
			their bike, it's almost guaranteed that they will shuffle the
			combo. So, it says that it's extremely unlikely to observe the true
			code while observing everything else is equally likely. This model
		is very naive.
		"""
		PROB = 1 / (10 ** digit_count)
		NO_PROB = 1 - PROB

		def prob_observation_given_actual(observation: int, actual: int) -> float:
			return PROB if observation == actual else NO_PROB

		return prob_observation_given_actual

	@staticmethod
	def create_distance_model(digit_count: int, distance_func: Callable = None, model_name: str = None,
							  enc_dist: bool = False) -> Callable:
		"""
		the distance model is a model such that the probability of observing
		O given that A is the true value grows as O is more different than
		A and shrinks as the two are more similar.

		Intuition:
			This model is based on the intuition that whenever someone shuffles
			their lock, they will try as much as possible to shy away from their
			true code. This, however, may not be exactly true and could be too
			generalizing. For example, one may always put the same exact code
			whenever they leave their bike.

		Note:
			We automatically store all distance models and then check whether
			they are stored in the first place before creating a new one

		:param distance_func:
			a function that takes in observation, actual, and digit_count
			and outputs how far observation is from actual (or vice versa)
		:param model_name:
			name of the model chosen when created or now
		:param enc_dist:
			this is a boolean that, if True, increases the probability of
			further distances. The choice of how to increase the probability
			linearly was made somewhat arbitrarily. See below.
		"""
		# try to load the model, if it fails, create it then save it
		try:
			distance_model_map = Models.load_model(model_name)
			assert distance_func is not None, 'we only store for non-null distance function'

			def prob_observation_given_actual(obs: int, actual: int) -> float:
				return distance_model_map[actual][distance_func(obs, actual, digit_count)]

			return prob_observation_given_actual
		except Exception as e:
			print('* failed to load model *')
			pass
		# if no distance function given, use the digit_distance function
		sample_space_size = 10 ** digit_count
		if distance_func is None:
			distance_func = Models.digit_distance
			mapping, multiplier = {}, 1
			for i in range(digit_count + 1):
				mapping[i] = utils.nCr(digit_count, i) * multiplier / sample_space_size
				multiplier *= 9

			def prob_observation_given_actual(obs: int, actual: int) -> float:
				return mapping[distance_func(obs, actual, digit_count)]

			# no need to store in this case because it's efficient enough
			return prob_observation_given_actual

		# get distance between all pairs for each potential actual, then
		# create a distribution to use for each.
		# WARNING: This is really inefficient and will take a very long time
		# runs in O(n^2), and n is usually in the set {10000, 100000}. so, we
		# amortize it by storing the model using the pickle package.
		prob_observation_given_actual_map: dict = {}
		# map distances to their encouraging distance to avoid multiple
		# computations.
		encouraging_distance = {}
		for actual in range(sample_space_size):
			mapping = {}
			for observation in range(sample_space_size):
				distance = distance_func(observation, actual, digit_count)
				# the encouraging distance was made such that it doesn't increase
				# too fast until it starts reaching really high values (around 16)
				if not distance in encouraging_distance:
					if enc_dist:
						encouraging_distance[distance] = 0
					else:
						encouraging_distance[distance] = int(distance ** 1.7 + (2.1 ** distance / 1000))
				mapping[distance] = mapping.get(distance, 0) + 1 + encouraging_distance[distance]
			# create a distribution to normalize the mapping
			temp_dist = Distribution(mapping)
			prob_observation_given_actual_map[actual] = {obs: temp_dist[obs] for obs in temp_dist}
			print('finished conditional of %d' % actual)

		def prob_observation_given_actual(obs: int, actual: int) -> float:
			distance = distance_func(obs, actual, digit_count)
			return prob_observation_given_actual_map[actual][distance]

		# store the model
		Models.store_model(prob_observation_given_actual_map, model_name)
		return prob_observation_given_actual

	@staticmethod
	def digit_distance(observation: int, actual: int, digit_count: int) -> int or float:
		"""
		return the number of digits that different from observation with actual.
		treat missing digits as 0. For example, if digit_count is 4 and observation
		is 53 and actual is 453, the difference is 2 because 0053 differs from 0453
		by 2 digits.

		using this as a distance function on the distance model is still naive because
		it doesn't account for the fact that although 5555 and 6666 differ by 4 digits,
		6666 is more similar to 5555 than 1234 is.
		"""
		obs_s = Models.extend_integer(observation, digit_count)
		act_s = Models.extend_integer(actual, digit_count)
		distance = 0
		for i in range(len(obs_s)):
			distance += 1 if obs_s[i] != act_s[i] else 0
		return distance

	@staticmethod
	def edit_distance(observation: int, actual: int, digit_count: int,
					  replace_cost_func: Callable = None) -> int or float:
		"""
		returns the number of edits needed to modify observation in order to get to
		actual.

		using this as a distance function sounds promising.

		:param replace_cost_func:
			this is a method that takes two argument, (character_origin (co), character_new (cn)),
			and gives the cost of changing co to cn.
		"""
		obs_s = Models.extend_integer(observation, digit_count)
		act_s = Models.extend_integer(actual, digit_count)
		if replace_cost_func is None:
			# the cost of changing co to cn is equal to the shortest length
			# in a rotating wheel that co is from cn if arranging digits
			# 0 through 9 in a wheel
			replace_cost_func = lambda co, cn: Models.replace_cost_by_rotations(co, cn)
		distance = 0
		for i in range(len(obs_s)):
			distance += replace_cost_func(act_s[i], obs_s[i])
		return distance

	@staticmethod
	def extend_integer(number: int, digit_count: int) -> str:
		"""
		Extend the number to become as long as digit_count but as a string
		"""
		assert type(number) == int, 'expecting a number, instead received -> ' + str(number)
		string_representation = str(number)
		while len(string_representation) < digit_count:
			string_representation = '0' + string_representation
		return string_representation

	@staticmethod
	def replace_cost_by_rotations(co: str or int, cn: str or int, cost_lower: int = 1, cost_higher: int = 1) -> int:
		"""
		return the cost by changing the digit one by one. this method is naive
		because it makes the following assumptions:
		- humans are efficient so they rotate their combo easiest way for each digit
		- humans don't rotate over the initial digit. i.e., they won't go once or more
			around the same digit in order to get to the resulting digit co.
		- humans rotate one digit at a time. some likely do, but not all, so this is not
			a reasonable assumption

		:param co: character original
		:param cn: character new
		:param cost_lower: cost of decreasing by 1
		:param cost_higher: cost of increasing by 1
		"""
		if type(co) == str:
			assert len(co) == 1, 'must be a single digit'
			co = int(co)
		if type(cn) == str:
			assert len(cn) == 1, 'must be a single digit'
			cn = int(cn)
		if co == cn:
			return 0
		# here, we're going down from co to cn, add 1 for
		# the cost of reaching 9 or 0 from 0 or 9 respectively
		lower = (co - cn if co > cn else co + 9 - cn + 1) * cost_lower
		# this is as if we're going down from cn to co,
		# add 1 for the same reason as above
		higher = (cn - co if cn > co else cn + 9 - co + 1) * cost_higher
		# assuming people are efficient
		return min(lower, higher)

	@staticmethod
	def store_model(model: dict, name: str) -> None:
		"""
		store the model by name
		"""
		pickle.dump(model, open('models/%s.pickle' % name, 'wb'))
		print('* distance model built and stored as %s *' % ('models/%s.txt' % name))

	@staticmethod
	def load_model(name: str) -> dict:
		"""
		load the model by name
		"""
		print('model loading as %s' % ('models/%s.pickle' % name))
		return pickle.load(open('models/%s.pickle' % name, 'rb'))
