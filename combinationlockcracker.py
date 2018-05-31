from distribution import Distribution
from typing import Callable, Iterable
from models import Models


class CombinationLockCracker:
	"""
	This class will be used to crack the code of a biker's lock.

	The idea is simple: a biker locks his bike with a lock on which there
	(usually) is a combination lock made of 4 to 5 digits. Let's assume
	one follows a specific biker and every time this biker locks his or
	her bike, one looks at the code combination left on the lock (which
	the biker will usually have shuffled: chances of not being shuffled are
	very low) and records that code. One does that multiple times with the
	same biker. In addition, one ensures that this is not the true combo by
	testing whether it unlocks. Let's assume it never unlocks (because
	otherwise this whole code would be useless).

	Then, this class has a method that will observe the list of code and
	internally make computations to try to guess the biker's lock code.

	The big statement (and goal) in this project is to be able to crack the
	actual code with at most 20 total readings. By crack, I mean reduce
	the number of "evident" possibilities to less than a threshold number,
	say somewhere between 20 to 100.
	"""

	def __init__(self, digit_count: int, observation_model: Callable, observations: list = None) -> None:
		"""
		initialize the combination lock cracker

		:param digit_count: the number of digits in the combination
		:param observation_model:
			a function of two parameters, obs and key. This returns the
			probability of observing obs given key is the true code.
		:param observations: a list of strings representing observations
		"""
		self._digit_count: int = digit_count
		self._possible_combinations = {i for i in range(10 ** digit_count)}
		self.obs_model = observation_model
		self._observations: list = []
		self._dist: Distribution = None
		self.build_distribution()
		self.observe_list(observations)

	def build_distribution(self, reset: bool = False) -> None:
		# distribution class will normalize
		self._dist = Distribution({i: 1 for i in range(10 ** self._digit_count)})
		if reset:
			self._observations = []

	def observe_list(self, observations: Iterable = None) -> None:
		"""
		based on a list of observations, update our belief about the
		code. We will always observe through a list and not directly
		observe an observation.

		:param observations: a list of strings representing lock combinations observed
		"""
		success_count, failure_count = 0, 0
		if observations is None:
			return
		# ensure we can iteration through observations
		assert isinstance(observations, Iterable), 'observations must be iterable'
		for obs in observations:
			try:
				self._observe(obs)
				success_count += 1
			except:
				failure_count += 1
				print('missed observation -> ' + str(obs))
		print("observed %d out of %d" % (success_count, success_count + failure_count))

	def _observe(self, observation: str) -> None:
		"""
		update our believe based on the observation model given at initialization
		this is the most important method and depends heavily on the observation
		model. Given a good one, Bayesian update can result in great results.

		Note:
			This model of observing a single observation is greedy at its core.
			The reason is because it observes new observations, makes updates, but
			doesn't account to how this new observation relate to the previous
			ones.

		:param observation: a string representing a single observation
		"""
		# if the number is not a string, convert it to string
		# the following throws an error if we're given an
		# invalid number that cannot become a string
		if type(observation) == str:
			# ensure the length of it is correct, then observe
			assert len(observation) <= self._digit_count
			observation = int(observation)
		elif type(observation) == int:
			# observe it as a string to ensure it has the right length
			self._observe(str(observation))
			return
		else:
			raise AssertionError('invalid observation type')
		# now, update the distribution using bayesian update and
		# observation model given at initialization
		dist_copy = self._dist.copy()
		for el in self._dist:
			new_prob = self.obs_model(observation, el) * self._dist.prob(el)
			dist_copy.set(el, new_prob, normalize=False)
		dist_copy.normalize()
		self._dist = dist_copy

	def reset(self) -> None:
		"""
		reset the whole set of observations and distribution
		"""
		self.build_distribution(reset=True)

	def modes(self) -> list:
		"""
		return the mode(s) of the distribution
		"""
		return self._dist.modes()

	def prob(self, code: int) -> float:
		"""
		Returns the probability of getting the given code after all
		the observations made.
		"""
		return self._dist.prob(code)

	def most_probables(self, count: int) -> dict:
		"""
		return the most probable codes after having made all the observations

		:param count: how many to include in the set of most probable codes
		"""
		most_probable = self._dist.most_probable(count)
		return {el: self._dist.prob(el) for el in most_probable}

	def digit_prob(self, index: int, digit: int) -> float:
		"""
		return the probability of seeing digit at the index given
		todo - implement this
		"""
		assert index < self._digit_count, 'index must be less than the digit count -> %s >= %s' \
										  % (str(index), str(self._digit_count))
		assert 0 <= digit < 10, 'digit must be in the range [0, 9] -> %d' % digit
		raise NotImplementedError

	def most_probable_digits(self, count: int) -> dict:
		"""
		same as most_probables, except this is for each digit in the code

		:param count:
			how many to include for each index in the set of most probable digits
		todo - implement this
		"""
		raise NotImplementedError

	def most_probable_adjacent(self, count: int, max_distance: int = 2) -> dict:
		"""
		for each element el, we will edit it by 1 and 2 (in the edit distance
		model--see Models in models.py) and assign them value prob/2 and prob/3
		respectively. Then, sum up every single one of those transitions (or
		adjacencies). Then, create a distribution out of the "histogram" created

		:param count:
			how many to include for each index in the set of most probable digits
		:param max_distance:
			the maximum distance is how far to get the adjacency. So, if it's 3,
			then for each element el, we will look at all codes distant by 1
			from el, distant by 2, then distant by 3.
		"""
		histogram = {}
		# calibrate the maximum distance to be limited
		# to 9 and ensure it's an integer
		max_distance = int(max(min(max_distance, 9), 1))
		for el in range(10 ** self._digit_count):
			s_el = Models.extend_integer(el, self._digit_count)
			prob = self.prob(el)
			histogram[el] = histogram.get(el, 0) + prob
			# add histogram for changes for each valid edit_distance
			for edit_distance in range(1, max_distance + 1):
				for el_with_edit in CombinationLockCracker.generate_edits(s_el, distance=edit_distance):
					i_el = int(el_with_edit)
					histogram[i_el] = histogram.get(i_el, 0) + (prob / edit_distance)
		# finally, return the most probable from a new
		# distribution created through the histogram
		dist = Distribution(histogram)
		most_probable = dist.most_probable(count)
		return {el: dist.prob(el) for el in most_probable}

	@staticmethod
	def generate_edits(s_el: str, distance=1, no_use_set=None) -> set:
		"""
		generates all possible edits by the distance given of the string
		integer s_el.

		:param s_el: string representing a lock combination
		:param distance: the desired distance from the initial number
		:param no_use_set:
			set containing all the edits not to use in the returned set
		"""
		if no_use_set is None:
			no_use_set = {s_el}
		if distance < 1:
			return {s_el}
		# create edit by 1
		edits_by_1 = set()
		for i in range(len(s_el)):
			digit = int(s_el[i])
			edits_by_1.add(s_el[:i] + str((digit + 1) % 10) + s_el[i + 1:])
			edits_by_1.add(s_el[:i] + str((digit - 1) % 10) + s_el[i + 1:])
		# generate edits recursively
		all_edits = set()
		for el in edits_by_1:
			others = CombinationLockCracker.generate_edits(el, distance - 1, no_use_set)
			all_edits |= others
		# remove the ones that we don't want in the result,
		# and update what the no_use_set contains as well
		if distance > 1:
			no_use_set |= edits_by_1
		return all_edits - no_use_set
