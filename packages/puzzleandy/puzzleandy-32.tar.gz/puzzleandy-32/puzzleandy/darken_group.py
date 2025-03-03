def darken(b,t):
	return np.minimum(b,t)

def multiply(b,t):
	return b*t

def color_burn(b,t):
	invalid = np.geterr()['invalid']
	np.seterr(invalid='ignore')
	r = np.where(
		b == 1,1,np.where(
		t == 0,0,1-np.minimum((1-b)/t,1)))
	np.seterr(invalid=invalid)
	return r

def linear_burn(b,t):
	return np.maximum(b+t-1,0)

def darker_color(b,t):
	bY = rgb_to_gray(b).atleast_3d()
	tY = rgb_to_gray(t).atleast_3d()
	return np.where(bY < tY,b,t)