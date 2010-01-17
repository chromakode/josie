import re

import app
import error
import game
import primitives
from parse import core_regex, constructor_param_regex
from macro import parse_macros

def traverse(data, func, *args):
	if type(data) is dict:
		newdata = dict()
		for key, value in data.iteritems():
			newdata[key] = traverse(value, func, *args)
		return newdata
	elif type(data) is list:
		newdata = list()
		for item in data:
			newdata.append(traverse(item, func, *args))
		return newdata
	elif type(data) is tuple:
		newdata = list()
		for item in data:
			newdata.append(traverse(item, func, *args))
		return tuple(newdata)
	else:
		return func(data, *args) or data

# Placeholder class for differentiating pickling
class SavedID(str):
	pass
	
class World:
	
	def __init__(self):
		self.vars = dict()
		self.objects = dict()
		
		self.source = None
		self.protagonist = None
		
	def __getstate__(self):
		def substitute_ids(data, world):
			# Recursively take objects and replace them with their ids
			if isinstance(data, primitives.Object):
				# Try to find an id for the object, if none found; ignore it
				# This is because some placeholder objects like Exits and RoomDetails are not registered, and are created by their parent objects
				try:
					id = world.get_id(data)
					return SavedID(id)
				except ValueError:
					return None
			else:
				return data
		
		def pack_data(world):
			# Pack up our data
			objectdata = dict()
			for id, object in world.objects.iteritems():
				objectdata[id] = (object.vars, object.location)
			data = (world.source.__name__, world.vars, objectdata)
			return traverse(data, substitute_ids, world)
		
		def find_changes(new, old):
			# Find the changes between two dictionaries, return a dictionary of only changed keys
			if type(new) is list and type(old) is list:
				changed = list()
				for newitem, olditem in zip(new, old):
					changed.append(find_changes(newitem, olditem))
				return changed
			if type(new) is tuple and type(old) is tuple:
				changed = list()
				for newitem, olditem in zip(new, old):
					changed.append(find_changes(newitem, olditem))
				return tuple(changed)
			elif type(new) is dict and type(old) is dict:
				changed = dict()
				for key in new:
					if key in old:
						if not new[key]==old[key]:
							changed[key] = find_changes(new[key], old[key])
					else:
						changed[key] = new[key]
				return changed
			else:
				return new
					
			return changed
		
		# Reload the source file to check original values
		sourceworld = World()
		sourceworld.load(self.source)
		
		# Figure out what's changed
		data = find_changes(pack_data(self), pack_data(sourceworld))
		
		return data
		
	def __setstate__(self, data):
		self.vars = dict()
		self.objects = dict()
		
		# Load the world file from which the saved game originated	
		self.load(__import__(data[0]))
		
		# Recursively take ids and replace them with existing objects
		def substitute_objects(data):
			if isinstance(data, SavedID):
				# Try to find an id for the object, if none found; ignore it
				# This is because some placeholder objects like Exits and RoomDetails are not registered, and are created by their parent objects
				try:
					object = self.get_object(data)
					return object
				except ValueError:
					return None
			else:
				return data
		
		data = traverse(data, substitute_objects)
		sourcename, vars, objectdata = data
			
		# Restore information to world
		self.vars.update(vars)
		for id, data in objectdata.iteritems():
			vars, location = data
			myobject = self.get_object(id)
			
			myobject.vars.update(vars)
			if location:
				myobject.move_to(location)
			
		self.protagonist = self.get_object(self.vars["PROTAGONIST"])
			
	def new_object(self, type, id):
		# MAGIC!
		def create(*args):
			self.objects[id] = primitives.get(type)(*args)
			return self.objects[id]
		return create
			
	def get_object(self, id):
		return self.objects[id]
	
	def get_id(self, object):
		return self.objects.keys()[self.objects.values().index(object)]
	
	def load(self, worldobject):
		self.source = worldobject
		
		if not app.version_at_least(self.source.META["app-version"]):
			raise error.VersionError(app.VERSION, self.source.META["app-version"])
		
		data = self.source.WORLD
		data = data.replace("\t", "")
		
		# Filter out comments
		data = core_regex["comment"].sub("", data)
		
		# Parse globals
		globals, objects = data.split("---")
		for match in core_regex["var"].finditer(globals):
			var, value = match.groups()
			self.vars[var] = value
		
		objects_with_params = list()
		# Parse and create objects
		# Stage 1: create objects
		for type, id, name, description, params in core_regex["constructor"].findall(objects):
			if not type in primitives.registry:
				# FIXME
				print "Error: Invalid type specified for object."
			
			newobject = primitives.get(type)(name, description)
			
			macro = parse_macros(newobject, description)
			if macro:
				newobject.get_description = macro
			
			if params:
				objects_with_params.append((newobject, params))
			
			self.objects[id] = newobject
		
		# Stage 2: set up objects that have additional parameters
		for object, params in objects_with_params:
			for param in constructor_param_regex["param"].findall(params):
				if isinstance(object, primitives.get("ROOM")):
					match = constructor_param_regex["exit"].match(param)
					if match:
						direction, destinationid = match.groups()
						object.add_exit(direction, self.get_object(destinationid))
				
				match = constructor_param_regex["var"].match(param)
				if match:
					var, value = match.groups()
					
					# We will use magic to match an (objectid) specifier, a list of (objectid)s, or a python expression.
					objectmatch = core_regex["object"].match(value)
					if objectmatch:
						object.vars[var] = self.get_object(objectmatch.groups()[0])
					elif core_regex["object_list_pattern"].match(value):
						object.vars[var] = [self.get_object(objectmatch.groups()[0]) for objectmatch in core_regex["object"].finditer(value)]
					else:
						# Otherwise, evaluate a python expression.
						object.vars[var] = eval(value, vars(self.source))
				
				match = constructor_param_regex["message"].match(param)
				if match:
					name, message = match.groups()
					
					macro = parse_macros(object, message)
					if macro:
						object.messages[name] = macro
					else:
						object.messages[name] = message
					
				match = constructor_param_regex["object"].match(param)
				if match:
					objectid = match.groups()[0]
					self.get_object(objectid).move_to(object)
			
		# Allow objects to set themselves up after they have been initialized.
		for object in self.objects.itervalues():
			if hasattr(object, "post_init"):
				object.post_init()
		
		self.protagonist = self.get_object(self.vars["PROTAGONIST"])
		self.protagonist.move_to(self.get_object(self.vars["START"]))

def load(worldsource):
	world = World()
	world.load(worldsource)
	return world
