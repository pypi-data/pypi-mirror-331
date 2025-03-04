#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform vec3 iResolution;

// red, yellow, cyan, green, blue, magenta
uniform float factors[6];

out float fragColor;

float lerp(float x, float f0, float f1)
{
	float fx = (1-x)*f0+x*f1;
	return fx;
}

void main()
{
	vec2 uv = fragCoord/iResolution.xy;
	vec3 hsl = texture(iChannel0,uv).xyz;
	vec3 lab = texture(iChannel1,uv).xyz;
	float h = hsl.x;
	float s = hsl.y;
	float v = hsl.z;
	float l = lab.x;
	int i = int(floor(h/60));
	float t = mod(h,60)/60;
	float factor = lerp(t,factors[i],factors[(i+1)%6]);
	fragColor = factor*s;
}