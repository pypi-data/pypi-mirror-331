import numpy as np

def to_float(x):
	x = np.clip(x/255,0,1)
	return x.astype(np.float32)

def to_uint(x):
	x = np.clip(x*255,0,255)
	return x.astype(np.uint8)