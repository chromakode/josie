import random

from engine import game, primitives, reality
from library import npc

META =	{
		
		"name": "Ocean",
		"description": "A thrilling quest to find the ocean.",
		"version":"0.1",
		"app-version": "0.2"
		
		}
		
WORLD = """
<PROTAGONIST: you>
<START: start>
---

HERO(you) Ryland
You look kind of ridiculous.
{
	<aliases: ["me", "self"]>
	<quips:	{
				"your mom":"Your mom's mom.",
				"ls":"Ye olde harddrive is empty.",
				"cheat":"How did you expect to cheat, anyway?",
				"omg":"ya i no.",
				"help":"Type in stuff to make cool stuff happen.",
				"yes":"I agree."
			}>
	"huh=[%:What?|Huh?|You don't say.|Fascinating.|Help! I cant understand you!|Are you speaking Eskimo?|Far out.]"
}

THINGY(trash) Piece of Trash
This is a piece of trash.
{
	<aliases: ["trash", "rubbish"]>
	"eat=[random.randint(0,1)==1:This trash tastes delicious.|The trash tastes terrible!]"
	"talk=$thing: That's what she said!"
}

ROOM(start) Outside
You are outside. There is some dirt here, and a nice little patch of grass[(trash)?: with some trash sticking out of it]. [reality.is_daytime()==True:It is a bright, sunny day|It's kind of dark out].
{
	Left->(left1)
	(trash)
	<details: {
				"up":"You see the sky.",
				"down":"Kind of dirty."
			}>
	<described: [(trash)]>
}

ROOM(left1) Left
There is some more dirt here.
{
	Left->(left2)
	Right->(start)
}

ROOM(left2) Left, Again
There is a dirty signpost here.
{
	Left->(left3)
 	Right->(left1)
	(sign1)
	<described: [(sign1)]>
}

SIGN(sign1) Sign
<-- Ocean that way.
{"heavy=Read the sign, silly!"}

ROOM(left3) Corale
There is an average-sized tarantula in an average-sized corale. Note that although they are both average size, they are not actually the same size. There is also a bucket near the corale[(note1)?: with a note attached to it].
{
	Right->(left2)
	(note1)(tarantula)
	<described: [(note1), (tarantula)]>
	#~ The tarantula will be milked by typing 'milk tarantula'. However, using the bucket on it will kill it. Or something... ~#
}

NPC_MARKOV(tarantula) Tarantula
An average-sized tarantula.
{
	<nametype: "thing">
	<markov:	{
				"chmrrr":{"sk": 1},
				"sk":{"vk": 1},
				"gff":{"vk": 1},
				"chzzz!!":{"~end~": 1},
				"mrxk!!":{"~end~": 1},
				"gfff":{"~end~": 1},
				"ry":{"milk": 1, "an": 1},
				"mrxk":{"vk": 1, "~end~": 1},
				"an":{"vk": 1, "~end~": 2},
				"vk":{"ry": 2, "mrxk!!": 1, "an": 1},
				"milk":{"chzzz!!": 1, "gff": 1, "gfff": 1},
				"~start~":{"mrxk": 2, "an": 1, "milk": 2, "chmrrr": 1}
				}>
	<quips: {"milk tarantula":"tiger bike."}>
}

NOTE(note1) Note
It reads: Please milk my tarantula while I'm away. Thanx.
{"heavy=Um, you're supposed to read it."}

THINGY(baguette) Baguette
Since you are a computer game character, you do not require food, so this is 
really just taking up space in your inventory.
{
	"eat=Mmm... carbs."
	"talk=You start a conversation with the the baguette. It responds in French."
	"kick=You kick the baguette. GOAL!"
}

THINGY(vanillacup) Vanilla Cup

THINGY(hairdye) Blue Hair Dye
{
	"eat=Nice going, now you have blue insides. Kind of like Kool-Aid."
	"talk=Oh, this is just sad."
	"kick=You have a blue foot."
}

"""

class Hero(primitives.Player):
	def __init__(self, name, description):
		primitives.Player.__init__(self, name, description)
		
		@self.add_command("talk", "talk$")
		def talk():
			game.output("You talk to yourself.")
		
primitives.add("HERO", Hero)	

# More detailed generic class
class Thingy(primitives.Thing):
	def __init__(self, name, description):
		primitives.Thing.__init__(self, name, description)
		
		self.messages.update({	"eat": "Try as you might, you cannot eat that.",
								"kick": "You kick the_$thing.",
								"talk": "Why are you talking to a $thing?"
							 })
		
		@self.add_command("eat", "eat [@me]")
		def eat():
			game.output(self.messages["eat"])
			
		@self.add_command("kick", "kick [@me]")
		def kick():
			game.output(self.messages["kick"](thing=self.name))
			
		@self.add_command("talk", "talk(?: to)? [@me]")
		def talk():
			game.output(self.messages["talk"](thing=self.name))
		
primitives.add("THINGY", Thingy)	

class Note(Thingy):
	def __init__(self, name, description):
		Thingy.__init__(self, name, description)
		self.messages.update({	"read": "The note says:\n$message",
							 	"kick": "The note flutters in the air.",
							 	"eat": "Mmm, paper.",
								"talk": "the_$thing asks you to read it."
							 })
		
		@self.add_command("read", "read$|read [@me]")
		def read():
			game.output(self.get_description())
			
		@self.add_command("kick", "kick [@me]")
		def kick():
			game.output(self.messages["kick"])
			
	def get_description(self):
		return self.messages["read"](message=self.description)
		
primitives.add("NOTE", Note)

class Sign(Note):
	def __init__(self, name, description):
		Note.__init__(self, name, description)
		self.messages.update({	"read": "The sign says:\n$message",
								"heavy": "You try to pull up the sign, but fail.",
							 	"kick": "Ouch, that hurt!",
							 	"eat": "Mmm, wood."
							 })
							 
		self.vars["heavy"] = True

primitives.add("SIGN", Sign)

class Tarantula(npc.NPC):
	def __init__(self, name, description):
		npc.NPC.__init__(self, name, description)
	
	def main(self):
		while 1:
			self.wait(1)
			#self.location.announce(self, "The Tarantula skitters.")
	
	def tell(self, msg):
		print msg

primitives.add("TARANTULA", Tarantula)
