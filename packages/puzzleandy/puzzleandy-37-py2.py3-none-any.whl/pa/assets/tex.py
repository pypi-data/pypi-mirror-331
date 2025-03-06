from importlib.resources import files
from pa.io import read

def load_tex(name):
	path = files()/'tex'/name
	return read(path)

def gradient():
	return load_tex('gradient.png')

def tie_dye():
	return load_tex('tie_dye.jpg')