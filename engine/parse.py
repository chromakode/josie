import re

save_file_regex = \
{
	"header": re.compile(r"\<(\w*)_v([\d\w\.]*): (\w*)_v([\d\w\.]*)\>")
}

core_regex = \
{	
	# World object description
	"constructor": re.compile(r"(\w*)\s*\((\w*)\)\s*(.*)\s*\n(.*)\s*(?:\{([\w\W]*?)\})?\n\n"),
	
	# Comment block
	"comment": re.compile(r"#~.*~#"),
	
	# Splits lists of closed <>, [], "", () entities
	"block": re.compile(r"\<.*?\>|\[.*?\]|\".*?\"|\(.*?\)"),
	
	# (objectid) reference
	"object": re.compile(r"\(([\w]*)\)"),
	"object_list_pattern": re.compile(r"\[(\(([\w]*?)\)\s*,?\s*?)+\]"),
	
	# Variable assignment
	"var": re.compile(r"<(\w*)\s*:\s*([\w\W]*?)>"),
	
	# Macro block
	"macro": re.compile(r"\[(.*?)\]")
}

constructor_param_regex = \
{
	"param": re.compile(r"\s*(\<.*?\>|\[.*?\]|\".*?\"|\(.*?\)|.*?\->\([\w]*?\))", re.DOTALL),
	"object": core_regex["object"],
	"exit": re.compile(r"(.*?)\->%s" % core_regex["object"].pattern),
	"var": core_regex["var"],
	"message": re.compile(r"\"(\w*)=(.*)\""),
}

message_substitute_regex = \
{
	"keyword": re.compile(r"(?:(a|the)_)?\$(\w*)")
}
