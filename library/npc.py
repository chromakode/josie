import time
import threading
import random

from engine import english, primitives

class NPC(primitives.Container, primitives.Thing):
	def __init__(self, name, description):
		primitives.Container.__init__(self, name, description)
		primitives.Thing.__init__(self, english.HumanName(name), description)
		
		self.messages.update({	"say": "the_$me says: $msg"	})
		
	def say(self, msg):
		self.location.announce(self, self.messages["say"](me=self.name, msg=msg))
		
primitives.add("NPC", NPC)

class QuipsNPC(NPC):
	def __init__(self, name, description):
		NPC.__init__(self, name, description)
		
		self.vars["quips"] = dict()
		
	def tell(self, text):
		if text in self.vars["quips"]:
			self.say(self.vars["quips"][text])
			return True

primitives.add("NPC_QUIPS", QuipsNPC)


class RandomNPC(QuipsNPC):
	def __init__(self, name, description):
		QuipsNPC.__init__(self, name, description)
		
		self.vars["phrases"] = list()
		
	def tell(self, text):
		if self.vars["phrases"]:
			self.say(random.choice(self.vars["phrases"]))

primitives.add("NPC_RANDOM", RandomNPC)

class MarkovNPC(QuipsNPC):
	START_TOKEN = "~start~"
	END_TOKEN = "~end~"
	
	def __init__(self, name, description):
		QuipsNPC.__init__(self, name, description)
		
		# Default value
		self.vars["KEYWORD_MULTIPLIER"] = 3

	def walk_chain(self, curword=START_TOKEN, outputwords=[], said=""):
		weights = list()
		maxweight = 0
		for word, weight in self.vars["markov"][curword].iteritems():
			if said and (word in said or word == self.END_TOKEN):
				# Give keywords additional probability in the Markov chain.
				# In addition, give the END_TOKEN the same advantage, in order to reduce the tendency of loops.
				maxweight += weight*self.vars["KEYWORD_MULTIPLIER"]
			else:
				maxweight += weight
				
			weights.append((word, maxweight))
			
		toss = random.randint(1, maxweight)
		for word, weight in weights:
			if toss <= weight:
				choiceword = word
				break

		if choiceword == self.END_TOKEN:
			return english.proper_sentence(" ".join(outputwords))
		else:
			return self.walk_chain(choiceword, outputwords + [choiceword], said)
		
	def tell(self, text):
		if QuipsNPC.tell(self, text):
			return
		msg = self.walk_chain()
		self.say(msg)
		
primitives.add("NPC_MARKOV", MarkovNPC)
