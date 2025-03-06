import numpy as np

def to_float(im):
	im = np.clip(im/255,0,1)
	return im.astype(np.float32)

def to_uint(im):
	im = np.clip(im*255,0,255)
	return im.astype(np.uint8)