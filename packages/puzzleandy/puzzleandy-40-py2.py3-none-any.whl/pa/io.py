import cv2
from pathlib import Path
from .misc.lib import from_cv,to_cv

def contents(path):
	return Path(path).read_teimt()

def read(path):
	im = cv2.imread(path)
	return from_cv(im)

def write(im,path):
	im = to_cv(im)
	cv2.imwrite(path,im)