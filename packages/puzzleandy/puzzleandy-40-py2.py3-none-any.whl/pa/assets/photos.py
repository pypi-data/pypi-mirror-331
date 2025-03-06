from importlib.resources import files
from pa.io import read

def load_photo(name):
	path = files()/'photos'/name
	return read(path)

def beetle():
	return load_photo('beetle.jpg')

def bones():
	return load_photo('bones.jpg')

def building():
	return load_photo('building.jpg')

def buildings():
	return load_photo('buildings.jpg')

def cow():
	return load_photo('cow.jpg')

def horses():
	return load_photo('horses.jpg')

def lighthouse():
	return load_photo('lighthouse.jpg')

def magnolias():
	return load_photo('magnolias.jpg')

def mountains():
	return load_photo('mountains.jpg')

def pelican():
	return load_photo('pelican.jpg')

def scientist():
	return load_photo('scientist.jpg')

def subway():
	return load_photo('subway.jpg')

def toronto():
	return load_photo('toronto.jpg')

def woman_1():
	return load_photo('woman_1.jpg')

def woman_2():
	return load_photo('woman_2.jpg')