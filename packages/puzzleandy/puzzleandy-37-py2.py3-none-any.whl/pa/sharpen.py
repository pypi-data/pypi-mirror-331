from .blur import box_blur,gauss_blur

def box_sharpen(x,n):
	y = box_blur(x,n)
	return x-y+x

def gauss_sharpen(x,n=None,s=None):
	y = gauss_blur(x,n,s)
	return x-y+x