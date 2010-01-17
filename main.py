import sys
import getopt
import imp

import app
import config
import io_basic as io
from engine import error, game, world, primitives

app.config.register("main.last_game_save", False)
app.config.register("main.save_on_exit", True)

class GlobalCommands(primitives.Object):
	def __init__(self):
		primitives.Object.__init__(self, "System Commands", "Global System Command Listener")
		
		@self.add_command("quit", "quit|exit")
		def quit():
			save_and_quit()
		
		@self.add_command("save", "save")
		def save():
			game.save()
			io.output("Your game has been saved.")
			
		@self.add_command("system", "system")
		def system():
			run_system_world()

def load_world(world_name):
    return imp.load_source(world_name, "worlds/"+world_name+".py")

def run_system_world():
	# Switch to the system world temporarily, retaining the old world state.
	game.currentworld = game.world
	game.world = world.load(load_world("system"))
	
	io.output("--- Entering System World ---")
	game.world.protagonist.globalcommands = game.currentworld.protagonist.globalcommands
	game.world.protagonist.commands["look"]()
	
	while True:
		print
		try:
			cmd = io.input("> ")
		except (KeyboardInterrupt, EOFError):
			game.world = game.currentworld
			save_and_quit()
			
		if cmd in ("done", "leave"):
			break
		game.world.protagonist.do_command(cmd)
	
	io.output("--- Leaving System World ---")
	game.world = game.currentworld
	game.currentworld = None
	game.world.protagonist.commands["look"]()

def mainloop():
	while game.playing:
		print
		try:
			cmd = io.input("> ")
		except (KeyboardInterrupt, EOFError):
			save_and_quit()
		
		game.world.protagonist.do_command(cmd)

def save_and_quit():
	io.output("Bye.")
	
	# Return from the system world if we are in it
	if hasattr(game, "currentworld") and game.currentworld:
		game.world = game.currentworld
	
	if game.playing and app.config["main.save_on_exit"]:
		filename = game.save()
		io.output("--- Your game has been saved. ---")
		app.config["main.last_game_save"] = filename
	app.quit()

def init(worldobj):	
	# Set global input and output hooks
	io.init()
	game.output = io.output
	game.input = io.input
	
	game.start(worldobj)
	globalcommands = GlobalCommands()
	game.world.protagonist.globalcommands = globalcommands
	game.world.protagonist.commands["look"]()
	mainloop()

def usage():
	print "usage: main.py [--world=<worldfile>][--load=<savefile>]"

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hl:w:", ["help", "load=", "world="])
	except getopt.GetoptError:
		# print help information and exit:
		usage()
		app.quit()
		
	worldsource = None
	worldobj = None
	for option, argument in opts:
		if option in ("-h", "--help"):
			usage()
			app.quit()
		elif option in ("-w", "--world"):
			try:
				worldobj = world.load(load_world(argument))
			except error.VersionError, e:
				io.errormsg("This world file requires a newer version (%s) of this game." % e.required)
				app.quit()
		elif option in ("-l", "--load"):
			try:
				worldobj = game.load(argument)
			except error.VersionError, e:
				io.errormsg("This save file was made using a different version (%s) of this game." % e.required)
				app.quit()
			except error.FileFormatError, e:
				io.errormsg(e.message)
				app.quit()
	
	if not worldobj:
		if app.config["main.last_game_save"]:
			game.output("--- Resuming your previous game. ---")
			worldobj = game.load(app.config["main.last_game_save"])
		else:
			# Temporarily default to ocean. In the future, there will be a chooser in the system world.
			worldobj = world.load(load_world("ocean"))
	
	init(worldobj)
	
if __name__ == "__main__":
    main()
