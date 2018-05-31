from typing import Hashable, Callable
# parent, left, and right are methods to navigate around the heap
parent = lambda i: max((i - 1) // 2, 0)
left = lambda i, n: min(2 * i + 1, n)
right = lambda i, n: min(2 * i + 2, n)


class MaxHeapPriorityQueue:
	"""
	The purpose of this heap priority queue is to mainly return the
	@count largest elements (using the comparison determined with @key).
	so, this class was built with that purpose in mind. See __init__
	method.
	"""

	def __init__(self, count: int, key: Callable=lambda i: i, elements: list = None) -> None:
		"""
		initialize the max heap.
		:param count: the needed number of elements to return when calling .sorted()
		:param elements: a list of elements to already include in this heap
		:param key: a function mapping elements to numerical values to use for comparison
		"""
		self.count, self.key = count, key
		self.A = []
		if elements is not None:
			assert type(elements) == list, 'elements must be a list'
			for el in elements: self.insert(el)

	def insert(self, el: Hashable) -> None:
		"""
		insert an element into this heap priority queue
		"""
		self.A.append(el)
		self._heapify_up(len(self.A) - 1)

	def extract_max(self) -> Hashable:
		"""
		extract the maximum element from this heap priority queue
		"""
		assert len(self.A) > 0, 'cannot extract_max from an empty heap'
		if len(self.A) == 1: return self.A.pop(-1)
		self.A[0], self.A[len(self.A) - 1] = self.A[len(self.A) - 1], self.A[0]
		maximum_element = self.A.pop(-1)
		self._heapify_down(0)
		return maximum_element

	def _heapify_up(self, i: int) -> None:
		"""
		heapify the heap up from index i. Essentially move the elements
		up the heap in order to maintain the heap property. see Wikipedia:
		https://en.wikipedia.org/wiki/Heap_(data_structure)
		"""
		p = parent(i)
		if self.key(self.A[p]) < self.key(self.A[i]):
			self.A[p], self.A[i] = self.A[i], self.A[p]
			self._heapify_up(p)

	def _heapify_down(self, i: int) -> None:
		"""
		heapify the heap down from index i. Essentially move the elements
		down the heap in order to maintain the heap property. see Wikipedia:
		https://en.wikipedia.org/wiki/Heap_(data_structure)
		"""
		l, r = left(i, len(self.A) - 1), right(i, len(self.A) - 1)
		c = l if self.key(self.A[r]) < self.key(self.A[l]) else r
		if self.key(self.A[i]) < self.key(self.A[c]):
			self.A[c], self.A[i] = self.A[i], self.A[c]
			self._heapify_down(c)

	def sorted(self) -> list:
		"""
		return @self.count largest elements in this heap. Note that this
		method renders the heap obsolete. It removes all data from the heap.
		runs in O(@self.count).
		"""
		sorted_list = []
		while True:
			try:
				sorted_list.append(self.extract_max())
				if len(sorted_list) == self.count:
					# remove all elements from the heap then return
					self.A = []
					return sorted_list[::-1]
			except AssertionError:
				# remove all elements from the heap then return
				self.A = []
				return sorted_list[:self.count][::-1]
