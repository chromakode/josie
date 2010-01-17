from string import capitalize, punctuation

from parse import message_substitute_regex

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

def capitalize_words(text):
	ignore_words = ["a", "and", "or", "of", "the", "with"]
	
	words = list()
	for index, word in enumerate(text.split(" ")):
		if word not in ignore_words or index==0:
			words.append(capitalize(word))
		else:
			words.append(word)
	
	return " ".join(words)
	
def proper_sentence(text):
	text = capitalize(text)
	if text[-1] not in punctuation:
		text += "."
	return text

def format_list(l):
	if not l:
		return ""
	elif len(l) == 1:
		return l[0]
	else:
		return ", ".join(l[0:-1]) + " and " + l[-1]

class Message:
	def __init__(self, format):
		self.format = format
	
	def substitute(self, **keywords):
		output = str(self.format)
		for match in message_substitute_regex["keyword"].finditer(output):
			article, keyword = match.groups()
			if keyword in keywords:
				value = keywords[keyword]
				if isinstance(value, Name):
					if article == "the":
						text = value.definite()
					elif article == "a":
						text = value.indefinite()
					else:
						text = value.format()
				else:
					text = str(value)
				
				# Capitalize if we are at the beginning of the sentence
				if match.start() == 0:
					text = capitalize(text)
					
				output = output.replace(match.group(), str(text))
		return output
		
	def __call__(self, **keywords):
		return self.substitute(**keywords)
		
	def __str__(self):
		return self.substitute()
	
class MessageSet:
	def __init__(self):
		self.messages = dict()
	
	def __setitem__(self, name, format):
		self.messages[name] = Message(format)
	
	def __getitem__(self, name):
		return self.messages[name]
		
	def update(self, messages):
		for name, format in messages.iteritems():
			self[name] = format

class Name:
	def __init__(self, name, capitalized = False):
		self.name = name
		self.capitalized = capitalized
		self.definite_article = ""
		self.indefinite_article = ""
		
	def format(self, capitalized = False):
		output = self.name
		if capitalized or self.capitalized:
			output = capitalize_words(output)
		else:
			output = output.lower()
		return output

	def definite(self):
		if self.definite_article:
			return self.definite_article + " " + self.format()
		else:
			return self.format()
		
	def indefinite(self):
		if self.indefinite_article:
			return self.indefinite_article + " " + self.format()
		else:
			return self.format()

	def __str__(self):
		return self.format()
			
class ThingName(Name):
	def __init__(self, name, capitalized = False):
		Name.__init__(self, name, capitalized)
		
		self.definite_article = "the"
		if self.name[0] in vowels:
			self.indefinite_article = "an"
		else:
			self.indefinite_article = "a"

class ProperName(ThingName):
	def __init__(self, name):
		ThingName.__init__(self, name, True)

class HumanName(Name):
	def __init__(self, name):
		Name.__init__(self, name, True)

nametypes = {"thing":ThingName, "proper":ProperName, "human":HumanName}
