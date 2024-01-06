#version 330 core

uniform sampler2D tex;
uniform sampler2D noise_tex;
uniform sampler2D fire_tex;
uniform sampler2D stars_tex;
uniform float w;
uniform float h;
uniform float time;

in vec2 uv;
out vec4 f_color;

void main() {
    vec4 color = texture(tex, uv);
    vec4 render_color = color;
    
    float w20 = floor(uv.x*20.0);
    float h20 = floor(uv.y*20.0);

    float rand1 = time + (153.2*w20/(h20+1.73));
    float rand2 = time + (153.2*h20/(w20+1.73));
    
    bool star = false;
    
    for (float x = -5*w; x < 5*w; x += w) {
        if (texture(stars_tex, vec2(uv.x + x, uv.y)).a > 0) {
            star = true;
            render_color += texture(stars_tex, vec2(uv.x + x, uv.y)) * 0.1;
        }
    }
    
    for (float y = -5*h; y < 5*h; y += h) {
        if (texture(stars_tex, vec2(uv.x, uv.y + y)).a > 0) {
            star = true;
            render_color += texture(stars_tex, vec2(uv.x, uv.y + y)) * 0.1;
        }
    }
    
    if (star) {
        render_color.yz = render_color.yz*clamp(sin(rand1), 0.5, 1.0);
    	render_color.xy = render_color.xy*clamp(cos(rand1), 0.5, 1.0);
    }
    
    // for futur fire trail effect
    if (texture(fire_tex, uv).a > 0) {
        render_color = vec4(color.r, color.gb, color.a);
    }
    
    // fog effect
    float center_dist = distance(uv, vec2(0.5, 0.5));
    //vec2 fog_pos = vec2(uv.x, uv.y - time/15);
    vec4 fog_color = texture(noise_tex, uv);
    fog_color = vec4(fog_color.r * 1.5, fog_color.g, fog_color.b * 1.5, fog_color.a);
    render_color += fog_color * center_dist * 0.4;
    
    f_color = render_color;
}