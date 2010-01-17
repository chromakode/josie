from sys import stdout
from random import random
import time

def print_serial_simulated(text, cps = 62, jitter = None):
	text = str(text)
	if not text:
		return
	delay = 1.0/cps
	for char in text:
		if jitter:
			time.sleep(delay + delay*random()*jitter)
		else:
			time.sleep(delay)
		stdout.write(char)
		stdout.flush()
	stdout.write("\n")
	stdout.flush()
