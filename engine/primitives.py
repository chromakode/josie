import re

import game
import macro
import command
import english
import utils
		
class Object:
	def __init__(self, name, description):
		self.vars = dict()
		self.commands = dict()
		self.messages = english.MessageSet()
		self.name = name
		
		self.vars["aliases"] = list()
		
		self.description = description
		self.location = None
		
	def post_init(self):
		# Allow the world writer to override the name type of the object
		
		# Get the raw name text
		if isinstance(self.name, english.Name):
			name = self.name.name
		else:
			name = self.name
			
		# Override if applicable
		if self.vars.has_key("nametype") and self.vars["nametype"]:
			# Either a string or a custom name class may be specified.
			if type(self.vars["nametype"]) is str:
				self.name = english.nametypes[self.vars["nametype"]](name)
			elif issubclass(self.vars["nametype"], english.Name):
				self.name = self.vars["nametype"](name)
				
		# If no name type has been set either in the class or the override, default to ThingName.
		if not isinstance(self.name, english.Name):
			self.name = english.ThingName(name)
		
	def __getinitargs__(self):
		return (self.name.name, self.description)
		
	def add_command(self, name, regex, case_sensitive = False):
		def command_dec(func):
			self.commands[name] = command.new_command(self, name, regex, func, case_sensitive)
		return command_dec

	def get_name(self):
		return str(self.name)
		
	def get_description(self):
		return self.description
		
	def do_look(self):
		game.output(self.get_description())
		
	def move_to(self, dest):
		if self.location:
			self.location.leave_inside(self)
		dest.enter_inside(self)
		
class Thing(Object):
	def __init__(self, name, description):
		Object.__init__(self, name, description)
		self.vars["visible"] = True
		self.vars["heavy"] = False
		self.messages.update({ 	"heavy": "You cannot lift that.",
								"get": "You get a_$thing.",
								"drop": "You drop a_$thing.",
								"missing": "You don't have a_$thing!"
							 })
		
		@self.add_command("look_at", "look(?: at)? [@me]")
		def look_at():
			self.do_look()
			
		@self.add_command("get", "(?:get|take|pick up) [@me]")
		def get():
			if self.vars["heavy"]:
				game.output(self.messages["heavy"])
			else:
				self.move_to(game.world.protagonist)
				game.output(self.messages["get"](thing=self.name))
			
		@self.add_command("drop", "(?:drop|put down) [@me]")
		def drop():
			if self.location == game.world.protagonist:
				self.move_to(game.world.protagonist.location)
				game.output(self.messages["drop"](thing=self.name))
			else:
				game.output(self.messages["missing"](thing=self.name))
		
class Container(Object):
	def __init__(self, name, description):
		Object.__init__(self, name, description)
		
		self.inside = list()
		
	def is_inside(self, thing):
		return thing in self.inside
		
	def find_inside(self, name):
		for thing in self.inside:
			for alias in thing.vars["aliases"]+[str(thing.name)]:
				if alias.lower() == name.lower():
					return thing
		
	def enter_inside(self, thing):
		if thing.location is None:
			thing.location = self
			self.inside.append(thing)
	
	def leave_inside(self, thing):
		if thing.location is self:
			self.inside.remove(thing)
			thing.location = None

class Player(Container, Thing):
	def __init__(self, name, description):
		Container.__init__(self, name, description)
		Thing.__init__(self, english.HumanName(name), description)
		self.vars["visible"] = False
		self.vars["heavy"] = True
		
		self.globalcommands = None
		# Just another name for inside
		self.inventory = self.inside
		
		self.messages.update({	"heavy": "You try to pick yourself up, but fail.",
								"empty_handed": "You have nothing.",
								"say": "You say \"$msg\""
							 })
	
		@self.add_command("look", "l$|look(?: around)?$")
		def look():
			self.location.do_look()
			
		@self.add_command("say", "(?:\"|say )(.*)")
		def say(msg):
			# If the last character is a quote, remove it.
			if msg[-1] == "\"":
				msg = msg[:-1]
			game.output(self.messages["say"](msg=msg))
			self.location.announce(self, msg)
				
		@self.add_command("inventory", "i$|inv|inventory")
		def inventory():
			if self.inventory:
				game.output("You have: %s" % english.format_list([thing.get_name() for thing in self.inventory]))
			else:
				game.output(self.messages["empty_handed"])
		
		@self.add_command("die", "die")
		def die():
			game.output("You die.")
			game.game_over()
			
	def do_command(self, cmd):
		def try_cmd(object):
			for command in object.commands.values():
				m = command.get_regex().match(cmd)
				if m is not None:
					if command(*m.groups()): return True
			return False
		
		# Attempt to match the command in the following order:
		# The player, the player's location, items in the player's inventory, items in the player's location.
		listeners = [self, self.location] + self.inventory + self.location.inside
		if self.globalcommands:
			listeners.append(self.globalcommands)
		for thing in listeners:
			if try_cmd(thing): return
		
		# If no match has been found, look for and try do_huh methods on the player and the player's location
		if hasattr(self, "do_huh") and self.do_huh(cmd): return
		if hasattr(self.location, "do_huh") and self.location.do_huh(cmd): return
		
		# As a last ditch, output the player's huh message.
		game.output(self.messages["huh"])
		
	def do_huh(self, cmd):
		if self.vars["quips"] and cmd.lower() in self.vars["quips"]:
			game.output(self.vars["quips"][cmd])
			return True
		
	def tell(self, msg):
		game.output(msg)

class RoomDetail(Object):
	def __init__(self, name, description):
		Object.__init__(self, english.ThingName(name), description)
		
		@self.add_command("look_at", "look(?: at)? [@me]")
		def look_at():
			self.do_look()
	
class Exit(Object):
	def __init__(self, name, dest):
		Object.__init__(self, english.ThingName(name), "It's an exit leading to %s." % dest.get_name())
		self.dest = dest
		
		self.messages.update({	"go": "You walk $direction."	})
		
		@self.add_command("go", "(?:go )?(?:to )?[@me]")
		def go():
			game.output(self.messages["go"](direction=self.name) + "\n")
			game.world.protagonist.move_to(self.dest)
			game.world.protagonist.commands["look"]()

class Room(Container):
	
	def __init__(self, name, description):
		Container.__init__(self, english.ProperName(name), description)
		
		self.exits = list()
		self.vars["described"] = list()
		self.vars["details"] = list()
		
	def post_init(self):
		if self.vars["aliases"]:
			self.vars["aliases"].append("here")
		else:
			self.vars["aliases"] = ["here"]
		
		if self.vars["details"]:
			for name, description in self.vars["details"].iteritems():
				detail = RoomDetail(name, description)
				detail.move_to(self)
	
	def do_look(self):
		game.output(self.get_name())
		game.output(self.get_description())
		
		need_desc = filter(lambda t:	isinstance(t, Thing) and 
										t.vars["visible"] and 
										t not in self.vars["described"]
									, self.inside)
		if need_desc:
			game.output("There is %s here." % english.format_list([thing.name.indefinite() for thing in need_desc]))
		
		exits = self.get_exits()
		if exits:
			game.output("Exits: %s" % english.format_list([exit.get_name() for exit in exits]))
		
	def add_exit(self, name, destination):
		exit = Exit(name, destination)
		exit.move_to(self)
		self.exits.append(exit)
		
	def get_exits(self):
		return self.exits
		
	def announce(self, speaker, msg):
		for thing in self.inside:
			if thing is not speaker and hasattr(thing, "tell"):
				thing.tell(msg)
	
registry = {"PLAYER": Player, "THING": Thing, "CONTAINER": Container, "ROOM": Room, "EXIT": Exit}

def add(name, classobj):
	if not name in registry:
		registry[name] = classobj

def get(name):
	return registry[name]
