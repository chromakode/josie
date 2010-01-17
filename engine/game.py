# Global game state
import threading
import pickle
import bz2

import app
from engine import parse, error

GAME_INIT = -1
GAME_OVER = 0
GAME_PLAYING = 1

playing = GAME_INIT
world = None

# Hooks for system output and input
def dummy_output(text):
	print text
output = dummy_output

def dummy_input(prompt = "> "):
	return raw_input(prompt)
input = dummy_input

def start(myworld):
	global world, playing
	world = myworld
	playing = GAME_PLAYING
	
def game_over():
	global playing
	playing = GAME_OVER
	
# "Magic number" to denote save file format
MAGIC_NUMBER = "JOSIESAVE"

def save(filename = None):
	global world
	if not filename:
		filename = ("config/save/%s.save" % world.source.META["name"]).lower()
	data = pickle.dumps(world, pickle.HIGHEST_PROTOCOL)
	data = bz2.compress(data)
	data = MAGIC_NUMBER+("<%s_v%s: %s_v%s>\n" % (app.NAME, app.VERSION, world.source.META["name"], world.source.META["version"])) + data
	open(filename, "w").write(data)
	return filename
	
def load(filename):
	global world
	data = open(filename, "r").read()
	
	if not data[:len(MAGIC_NUMBER)] == MAGIC_NUMBER:
		raise error.FileFormatError("The file does not appear to be a save game file.")
	data = data[len(MAGIC_NUMBER):]
	
	header, data = data.split("\n", 1)
	
	match = parse.save_file_regex["header"].match(header)
	if not match:
		raise error.FileFormatError("Unable to read save file header.")
	
	appname, appversion, worldname, worldversion = match.groups()
	if not appname == app.NAME:
		raise error.FileFormatError("This file seems to have been saved using a different program.")
	if not app.version_equal(appversion):
		raise error.VersionError(app.VERSION, appversion)
	
	# Check world version using worlds repository here
	
	data = bz2.decompress(data)
	return pickle.loads(data)
	
