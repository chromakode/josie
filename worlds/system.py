import traceback

import app
from engine import game, english, primitives

META =	{
		
		"name": "System",
		"description": "The system configuration world.",
		"version": "0.1",
		"app-version": "0.2"
		
		}
		
WORLD = """
<PROTAGONIST: you>
<START: main>
---

PLAYER(you) Player
You are semi-transparent.
{
	<aliases: ["me", "self"]>
	<quips:	{
				"ls":"Ye olde harddrive is empty.",
				"help":"This is the system world. For instructions and information, use 'look around' and 'look [thing]' to find out more about each object. Type 'leave' or 'done' to return to your game.",
			}>
	"huh=[%:What?|Huh?|You don't say.|Fascinating.|Help! I cant understand you!|Are you speaking Eskimo?|Far out.]"
}

ROOM(main) System
Welcome to the system configuration world. From here, you can control certain aspects of the game, as well as change system-wide configuration options. Take a look at each object to find out more about what it does and how to use it.
{
	(you)
	debug->(debug)
	config->(configuration)
}

ROOM(configuration) Configuration
A clean white room with a simple table at the center. Atop the table is a piece of paper titled \"Config\".
{
	back->(main)
	(configpaper)
	<details: {
				"table":"A minimalistic white table."
			}>
	<described: [(configpaper)]>
}

CONFIGPAPER(configpaper) Piece of paper titled "\Config\"
A piece of paper titled "Config". Use 'change [field]' to write on it.
{
	<aliases: ["config", "paper"]>
}

ROOM(debug) Debug Land
This room is dark, filled with roaring mechanical chatter and blinking green and red lights. The place is festooned with wires. From here you may tear away the facade of reality and inspect its inner workings.
{
	back->(main)
	(pythonshell)
}

PYTHONSHELL(pythonshell) Python Shell
A tiny trapdoor where the universe's inner workings show through. Type 'activate python shell' to enter the Python Shell.
{
	<aliases: ["shell"]>
}

"""

class PythonShell(primitives.Thing):
	def __init__(self, name, description):
		primitives.Thing.__init__(self, name, description)
		
		self.messages.update({	"activate": "You activate the_$me.",
								"deactivate": "the_$me powers down.",
							 })
		
		@self.add_command("activate", "(?:activate|start|enter|use) [@me]")
		def activate():
			self.do_shell()
			
	def do_shell(self):
		game.output(self.messages["activate"](me=self.name))
		game.output("Type \"done\" to exit.")
		cmd = None
		while cmd != "done":
			if cmd:
				try:
					print repr(eval(cmd))
				except SyntaxError:
					try:
						exec cmd
					except:
						traceback.print_exc()
				except:
					traceback.print_exc()
			
			cmd = game.input(">>> ")
			
		game.output(self.messages["deactivate"](me=self.name))
						
primitives.add("PYTHONSHELL", PythonShell)

class ConfigPaper(primitives.Thing):
	def __init__(self, name, description):
		primitives.Thing.__init__(self, name, description)
		
		@self.add_command("read", "read [@me]")
		def read():
			game.output("The paper says:")
			game.output("=== Config ===")
			for section in app.config.sections():
				game.output("\n[%s]" % section)
				for key, value in app.config.items(section):
					game.output("%s.%s: %s" % (section, key, value))
					
		@self.add_command("change", "(?:change|set) [@thing](?: on [@me])?")
		def change(key):
			if app.config.has_key(key):
				value = game.input("Change to: ")
				
				# Convert what the user input to the previous value type of the setting
				keytype = type(app.config[key])
				value = keytype(eval(value))
				app.config[key] = value
				
				game.output("You write %s under %s." % (value, key))
			else:
				game.output("The paper has no field named %s." % key)
		
primitives.add("CONFIGPAPER", ConfigPaper)

