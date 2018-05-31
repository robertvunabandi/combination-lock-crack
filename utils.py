import math


def nCr(n, r):
	"""
	n choose r, see here: https://en.wikipedia.org/wiki/Binomial_coefficient
	"""
	return math.factorial(n) / math.factorial(r) / math.factorial(n - r)
