from ConfigParser import SafeConfigParser

defaults = {}
location = "config/josie.cfg"

class DictConfigParser(SafeConfigParser):
	def __init__(self, defaults, defaultsection="main"):
		SafeConfigParser.__init__(self, defaults)
		self.defaultsection = defaultsection
		
	def __splitkey(self, key):
		if "." in key:
			return key.split(".")
		else:
			return self.defaultsection, key
	
	def __getitem__(self, key):
		section, option = self.__splitkey(key)
		return eval(self.get(section, option))

	def __setitem__(self, key, value):
		section, option = self.__splitkey(key)
		return self.set(section, option, repr(value))

	def has_key(self, key):
		section, option = self.__splitkey(key)
		return self.has_option(section, option)
		
	def register(self, key, default):
		section, option = self.__splitkey(key)
		if not self.has_section(section):
			self.add_section(section)
		if not self.has_key(key):
			self[key] = default

def load():
	config = DictConfigParser(defaults)
	config.read([location])
	return config
