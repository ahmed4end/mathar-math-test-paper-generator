import re, random
#import engine

class Robot():

	MIN_RANDOM = 1
	MAX_RANDOM = 30
	MAX_RECURSION = 300
	SHUFFLE = True

	def prepare_samples(self, queue):
		res = []
		for q in queue:
			res.extend(list(self.generate(q))) 
			#del used keys.
			del q['raw']
			del q['rules']
			del q['face']
			del q['count']

		if self.SHUFFLE:
			random.shuffle(res)

		return res

	def generate(self, head):
		#init
		raw = head['raw']
		rules = head['rules']
		face = head['face']
		count = head['count']
		vars = self.extract_vars(raw)
		res = set()
		c = 0
		while len(res)<count and c<self.MAX_RECURSION:
			c += 1
			values = self.gen_random(vars)

			sample = self.replace_vars(face, values)

			if all([self.evaluate(self.replace_vars(i, values)) for i in rules]): # assure all rules are true.
				res.add(sample)

		if not len(res)==count:
			print(f'<ERROR>: only {len(res)} is made out of {count}.')

		return res

	def extract_vars(self, txt):
		return re.findall(r'[a-z]', txt)

	def gen_random(self, vars):
		return {v: random.randint(self.MIN_RANDOM, self.MAX_RANDOM) for v in vars}

	def replace_vars(self, txt, trans):
		for i, j in trans.items():
			txt = txt.replace(i, str(j))
		return txt

	def evaluate(self, exp):
		return eval(exp)


class Drawer:

	def __init__(self):
		pass

if __name__=='__main__':
	from pprint import pprint
	data = [
				{'raw': 'a/b', 'count': 5, 'face': 'f(a/b)', 'rules': ['(a/b)==int(a/b)', 'a!=b', 'b!=1']},
				{'raw': 'a**0.5', 'count': 5, 'face': 'r(a)', 'rules': []},
	]

	obj = Robot().prepare_samples(data)
	pprint(obj)


