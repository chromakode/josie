import re

import macro

class SelfNamesMacro(macro.Macro):
	pattern = re.compile(r"@me")
	static = False
	
	def evaluate(self, object):
		names = object.vars["aliases"] + [str(object.name)]
		articles = (object.name.definite_article, object.name.indefinite_article)
		
		return "(?:%s)?\s*(?:%s)" % ("|".join(articles), "|".join(names))
		
class ThingMacro(macro.Macro):
	pattern = re.compile(r"@thing")
	static = True
	
	def evaluate(self, object):
		return "(.+)"

command_macros = [SelfNamesMacro, ThingMacro]

class Command:
	def __init__(self, name, regex, func, case_sensitive = False):
		self.name = name
		self.regex = regex
		self.case_sensitive = case_sensitive
		self.func = func
		
	def get_regex(self):
		if self.case_sensitive:
			return re.compile(str(self.regex))
		else:
			return re.compile(str(self.regex), re.IGNORECASE)
	
	def __call__(self, *args, **kwargs):
		return self.func(*args, **kwargs)!=False

def new_command(object, name, regex, func, case_sensitive):
	new_regex = macro.parse_macros(object, regex, command_macros)
	if new_regex: regex = new_regex
	
	return Command(name, regex, func, case_sensitive)
	
