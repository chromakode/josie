import random
import re

import game
import parse

class Macro:
	pattern = None
	static = False
		
	def __init__(self, *args):
		self.args = args
		
	def process(self, object):
		return self.evaluate(object, *self.args)
	
class ContentsConditionalMacro(Macro):
	pattern = re.compile(r"%s\?:([^\|]*)\s*(?:\|(.*))?\s*" % parse.core_regex["object"].pattern)
	
	def evaluate(self, object, objectid, present, missing):
		thing = game.world.objects[objectid]
		if object.is_inside(thing) and thing.vars["visible"]:
			return present
		else:
			return missing
		
class VarConditionalMacro(Macro):
	pattern = re.compile(r"(<.*>|.*)(==|!=|>|<|>=|<=)(.*):([^\|]*)\s*(?:\|(.*))?\s*")
	
	def evaluate(self, object, varname, operator, expression, truemsg, falsemsg):
		if varname[0]=="<":
			expr = str(object.vars[varname[1:-1]]) + operator + expression
		else:
			expr = varname + operator + expression
		if eval(expr, vars(game.world.source)):
			return truemsg
		else:
			return falsemsg

class RandomChoiceMacro(Macro):
	pattern = re.compile(r"%:(.*)\s*")
	
	def evaluate(self, object, messages):
		return random.choice(messages.split("|"))


class MacroDeferral:
	def __init__(self, object, macrochain):
		self.object = object
		self.chain = macrochain
		
	def process(self):
		output = str()
		for item in self.chain:
			if type(item)==str:
				output += item
			else:
				output += item.process(self.object) or ""
		return output
				
	def __call__(self):
		return self.process()
		
	def __str__(self):
		return self.process()
	
default_macros = [ContentsConditionalMacro, VarConditionalMacro, RandomChoiceMacro]
	
def parse_macros(object, text, macros = default_macros):
	chain = list()
	matches = list()
	
	for block in parse.core_regex["macro"].finditer(text):
		for macro in macros:
			match = macro.pattern.match(block.groups()[0])
			start = block.start()
			end = block.end()
			if match:
				matches.append((macro, match, start, end))	
	if not matches:
		return None
	
	# Whether all matching macros can be applied immediately
	static = True
	# Offset to keep track of the length we have already cut off
	offset = 0
	for macro, match, start, end in matches:
		if not macro.static: static = False
		chain.append(text[:start-offset])
		chain.append(macro(*match.groups()))
		text = text[end-offset:]
		offset = end
	chain.append(text)
	
	deferral = MacroDeferral(object, chain)
	if static:
		return deferral.process()
	else:		
		return deferral
