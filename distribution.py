from heap_pq import MaxHeapPriorityQueue
from typing import Callable

class Distribution(dict):
	"""
	This class offers multiple methods to probabilistic
	distributions and manipulations.
	"""
	DELTA = 1e-8

	def __init__(self, dist: dict = None) -> None:
		"""
		initialize the distribution
		:param dist: dictionary mapping keys to numbers
		"""
		if dist is None: dist = {}
		assert type(dist) == dict, 'argument must be a dictionary'
		super(Distribution, self).__init__(self)
		for e in dist:
			assert type(dist[e]) == int or type(dist[e]) == float, 'distribution keys must be numbers'
			assert type(dist[e]) == float or type(dist[e]) == int, 'dictionary must map keys to numbers'
			self[e] = dist[e] + 0.0
		self.normalize()

	def normalize(self) -> None:
		"""
		normalize the dictionary
		if the dictionary is already normalize or empty, this does nothing
		"""
		total = sum(self.values())
		# ensure we are within Distribution.DELTA threshold
		if 1 - Distribution.DELTA < total < 1 + Distribution.DELTA:
			return
		for e in self: self[e] /= total

	def set(self, el: int or float, prob: float, normalize: bool=True) -> None:
		"""
		sets the probability of an element
		:param normalize: whether to normalize after setting this probability
		"""
		assert type(el) == float or type(el) == int, 'keys must be a numbers'
		assert type(prob) == float or type(prob) == int, 'prob must be a numbers'
		self[el] = prob + 0.0
		if normalize: self.normalize()

	def prob(self, el: int or float) -> float:
		"""
		return the probability of the given element
		"""
		return self[el]

	def __missing__(self, el: int or float) -> float:
		"""
		if an element is missing, we return 0
		"""
		return 0.0

	def modes(self) -> list:
		"""
		returns the values that achieve the highest probability in this
		distribution. If the distribution is empty, this returns None,
		otherwise, this returns a list of all the elements that achieve
		the highest distribution (in case of ties) or a list of 1 element
		"""
		modes = None
		for el in self:
			if modes is None:
				modes = [el]
			if self[el] > self[modes[-1]]:
				modes = [el]
			elif self[el] == self[modes[-1]]:
				modes.append(el)
		return modes

	def expectation(self) -> float:
		"""
		return the expectation of the distribution or 0 if empty
		"""
		expectation = sum([el * self.prob(el) for el in self])
		return expectation

	def projection(self, func: Callable):
		"""
		apply a function to all elements and translate the distribution
		onto a new space
		:param func: function to call on each elements for their mapped values
		"""
		dictionary = {}
		for el in self:
			mapped_el = func(el)
			dictionary[mapped_el] = dictionary.get(mapped_el, 0) + self[el]
		return Distribution(dictionary)

	def variance(self) -> float:
		"""
		return the variance of the distribution or 0 if empty
		"""
		expectation = self.expectation()
		dist = self.projection(lambda el: (el - expectation) ** 2)
		return dist.expectation()

	def most_probable(self, count: int or float) -> list:
		"""
		return the @count most probable elements in the distribution
		"""
		pq = MaxHeapPriorityQueue(count, key=lambda el: self[el])
		for el in self:
			pq.insert(el)
		return pq.sorted()

	@staticmethod
	def build_uniform_dist(keys: list):
		"""
		builds a uniform distribution from the keys given
		"""
		return Distribution({el: 1 for el in keys})

	def __copy__(self):
		"""
		makes a copy of the distribution and returns it
		"""
		dic = {el: self[el] for el in self}
		return Distribution(dic)

	def copy(self):
		"""
		see __copy__
		"""
		return self.__copy__()
