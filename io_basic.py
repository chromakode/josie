import threading
from sys import stdin, stdout
try:
	import readline
except ImportError:
	pass

import app
from utils import print_serial_simulated

app.config.register("io.use_serial_simulation", True)
app.config.register("io.serial_simulation_speed", 62)

# Prepare for multithreading, just in case
__output_lock = threading.RLock()
__input_lock = threading.RLock()

def init():
	# Nothing fancy
	pass
	
def output(text = "", fast = False):
	# Locking input somewhat unnecessary, though this may change.
	# Don't interrupt the user if they are typing.
	__input_lock.acquire()
	__output_lock.acquire()

	if app.config["io.use_serial_simulation"]:
		if fast:
			print text
		else:
			print_serial_simulated(text, app.config["io.serial_simulation_speed"])
	else:
		print text
	
	__output_lock.release()
	__input_lock.release()

def input(prompt = "> "):
	__input_lock.acquire()
	
	text = raw_input(prompt)
	
	__input_lock.release()
	return text

def errormsg(text):
	print "Error: " + text
