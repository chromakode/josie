import string
import sys

# We want to use libs from the parent directory
sys.path.append("..")
sys.path.append(".")

import io_basic as io
from library import npc

mybot = npc.MarkovNPC("MyBot", "MarkovGen Dummy Bot")
mybot.vars["markov"] = dict()

io.output("""\
Markov Chain Generator
Use this tool to create brains for Markov chain NPCs. Please enter sentences to "teach" the bot; do note that due to the nature of Markov bots, these words will be mashed up and rearranged once enough sentences have been entered. Shoot for at least 15-25 sentences. 

At any time, a blank line or "!say ___" will simulate speaking to the bot. Type "!quit" to exit (and output the Markov chains).
""", fast=True)

while 1:
	sentence = io.input("Add a sentence: ")
	
	if sentence == "!quit":
		break
	if sentence[0:4] == "!say" or sentence == "":
		if mybot.vars["markov"]:
			if sentence != "":
				said = sentence[4:]
			else:
				said = ""
			io.output("The bot says: " + mybot.walk_chain(said=said))
			continue
		else:
			io.output("Please add a sentence to the bot.")
			continue
					
	sentence = sentence.lower()
	wordlist = [mybot.START_TOKEN] + sentence.split(" ") + [mybot.END_TOKEN]
	
	for index, word in enumerate(wordlist):
		if word == "~end~":
			break
		nextword = wordlist[index+1]
		
		# Ensure the word is in our collection
		if word not in mybot.vars["markov"]:
			mybot.vars["markov"][word] = dict()
		
		# Increment or instantiate the tally of nextword following word.
		if nextword not in mybot.vars["markov"][word]:
			mybot.vars["markov"][word][nextword] = 1
		else:
			mybot.vars["markov"][word][nextword] += 1

# Sort the word groups
wordrecords = mybot.vars["markov"].items()
wordrecords.sort(key=lambda x: x[1])

# Magic formatted dump!
dump = "<markov:\t{\n" + ",\n".join(["\t\t%s:%s" % (repr(word), repr(records)) for word, records in wordrecords]) + "\n\t\t}>"
dump = dump.replace("'", "\"")
io.output("Add the following to your NPC_MARKOV object:")
io.output(dump)
