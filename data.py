import random


class LockCData:
	"""
	data loading and storing class

	The data folder is a folder for trying to figure out the true
	code given that we know it. It's the learning data essentially.
	We know the result, and we try to see how well the algorithm
	behaves.

	The validation_data folder has data, but it doesn't contain the
	true code for that data.

	Inside of each data file (with .txt extensions), stored in the
	data folder, the first line
	is:
		CODE:{true-combo},{digit_count}
	{true-combo} is a placeholder for the true combination.
	{digit_count} is a placeholder for the number of digits in the
	combination lock.
	Then, every subsequent line is an observation readings. There
	is no need to write leading zeros.

	Additionally, see LockCData.load_data for more information.
	"""

	@staticmethod
	def load_simulated(number: int) -> tuple:
		"""
		see load_data
		"""
		return LockCData.load_data('data/simulated_%d.txt', number)

	@staticmethod
	def load_observed(number: int) -> tuple:
		"""
		see load_data
		"""
		return LockCData.load_data('data/observed_%d.txt', number)

	@staticmethod
	def load_random(number: int) -> tuple:
		"""
		see load_data
		"""
		return LockCData.load_data('data/random_%d.txt', number)

	@staticmethod
	def load_data(template: str, number: int) -> tuple:
		"""
		load data based on template and number. all data files are named
		{category}_{number}.txt. The number is given as an argument, and
		the category is one of:
		- observed:
			meaning the data was recorded on a true bike for study purpose
		- random:
			meaning the data was randomly generated making sure not to
			match the true code
		- simulated:
			meaning the data was recorded by iterative shuffling of lock
			combo going from true code to shuffled code multiple times.
		:param template: a string of the form: 'data/{category}_%d.txt'
		:param number: the number on this category to load
		"""
		with open(template % number) as f:
			bundle = [line.strip('\n') for line in f.readlines()]
			code, digit_count = [int(el) for el in bundle[0].strip('CODE:').split(',')]
			data = [int(observation) for observation in bundle[1:]]
			return code, digit_count, data

	@staticmethod
	def generate_random_data(number: int, true_combo: int, digit_count: int) -> None:
		"""
		generate random data and store it with the appropriate name in
		the data folder.
		:param number: the file will be named 'data/random_{number}.txt'
		:param true_combo: the true code of the lock
		:param digit_count: the number of digits in the combo
		"""
		file = open('data/random_%d.txt' % number, 'w')
		bundle = ['CODE:%d,%d\n' % (true_combo, digit_count)]
		max_value = 10 ** digit_count
		for i in range(20):
			point = random.randint(0, max_value - 1)
			while point == true_combo:
				point = (point + random.randint(0, max_value - 1)) % max_value
			bundle.append(str(point) + ('\n' if i != 19 else ""))
		file.writelines(bundle)
		file.close()
