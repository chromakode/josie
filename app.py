import sys

import config as _config

NAME = "Josie"
VERSION = "0.2.2"

# Load system configuration
config = _config.load()

def version_at_least(required):
	return VERSION.split(".") >= required.split(".")

def version_equal(required):
	return VERSION.split(".") == required.split(".")

def quit():
	config.write(open(_config.location, "w"))
	sys.exit()
