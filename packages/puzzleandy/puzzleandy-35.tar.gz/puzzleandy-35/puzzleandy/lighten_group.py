# lighten group

def lighten(b,t):
	return np.maximum(b,t)

def screen(b,t):
	return b+t-b*t

def color_dodge(b,t):
	invalid = np.geterr()['invalid']
	np.seterr(invalid='ignore')
	r = np.where(
		b == 0,0,np.where(
		t == 1,1,1-np.minimum(b/(1-t),1)))
	np.seterr(invalid=invalid)
	return r

def linear_dodge(b,t):
	return np.minimum(b+t,1)

def lighter_color(b,t):
	bY = rgb_to_gray(b).atleast_3d()
	tY = rgb_to_gray(t).atleast_3d()
	return np.where(bY < tY,t,b)