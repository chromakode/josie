import time

def is_daytime():
	hour = time.localtime()[3]
	return hour > 7 and hour < 19
