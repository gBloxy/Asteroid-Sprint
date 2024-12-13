#version 330 core

uniform sampler2D tex;
uniform sampler2D noise_tex;
uniform sampler2D fire_tex;
uniform sampler2D stars_tex;
uniform sampler2D ui_surf;
uniform vec3 sts[5];
uniform int max_st;
uniform float w;
uniform float h;
uniform vec2 res;
uniform float time;
uniform bool game_over;
uniform vec2 player_pos;
uniform float repulse_ti;
uniform float shield;
uniform int max_magnet;
uniform int max_freeze;
uniform int magnet;
uniform int freeze;
uniform bool menu;
uniform vec2 mouse;

const vec4 bkg_color = vec4(0.0392, 0., 0.2352, 1.);
const vec2 grid_size = vec2(25.);

in vec2 uv;
out vec4 f_color;


void main() {
    vec4 color = bkg_color;
    vec4 render_color = color;
    
    // velocity effects
    
    int delay;
    float lum;
    
    if (magnet > 0) {
        delay = max_magnet - magnet;
        lum = delay * 0.06;
    }
    else {
        lum = 5.;
    }
    
    if (freeze > 0) {
        delay = max_freeze - freeze;
    }
    
    // make stars shine
    
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
    
    for (float y = -5*h; y < lum*h; y += h) {                               // "lum": very slow. slow down fps to 35.
        if (texture(stars_tex, vec2(uv.x, uv.y + y)).a > 0) {               // replace by "5" to remove stars magnet effect
            star = true;
            render_color += texture(stars_tex, vec2(uv.x, uv.y + y)) * 0.1;
        }
    }
    
    if (star) {
        render_color.yz = render_color.yz*clamp(sin(rand1), 0.5, 1.0);
    	render_color.xy = render_color.xy*clamp(cos(rand1), 0.5, 1.0);
    }
    
    // fog effect
    
    float center_dist = distance(uv, vec2(0.5, 0.5));
    
    vec2 fog_pos = uv / 1.5;
    if (! game_over) {
        fog_pos.y -= time * 0.16;
    }
    else {
        fog_pos.y -= time * 0.055;
        fog_pos.x -= time * 0.03;
    }

    vec4 fog_col = texture(noise_tex, fog_pos);
    
    if (magnet > 0){
        fog_col = vec4(fog_col.r + 0.0002 * delay, fog_col.gba);
    }
    else if (freeze > 0) {
        fog_col = vec4(fog_col.r, fog_col.g + 0.0003 * delay, fog_col.b + 0.0002 * delay, fog_col.a);
    }
    else {
        fog_col = vec4(fog_col.r * 1.15, fog_col.g, fog_col.b * 1.35, fog_col.a);
    }
    
    render_color += fog_col * center_dist * 0.5;
    
    // render game
    
    vec4 game_col = texture(tex, uv);
    
    if (game_col.a > 0. && !menu) {
        render_color = mix(color, game_col, game_col.a);
    }
    
    // render stellar credits
    
    for (int i; i<max_st; i++) {
        vec2 pos = sts[i].xy;
        if (pos == vec2(-1.)) {
            continue;
        }
        pos = pos / res;
        float dist = distance(pos, uv);
        vec2 radius_vec = vec2(sts[i].z) / res * 3.5;
        float radius = radius_vec.x;
#if 0
        render_color += vec4(1.0, 0.8431, 0., 1.) *  (1 / dist) * 0.02;
#elif 0
        if (dist < radius) {
            render_color += vec4(0.8, 0.67448, 0., 1.) *  (1 / dist) * 0.02; // vec4(1.0, 0.8431, 0., 1.)
        }
        else {
            render_color += vec4(0.8, 0.67448, 0., 1.) *  (1 / dist) * 0.007;
        }
#elif 0
        dist = max(dist, 0.001);
        float attenuation = 1.0 / (1.0 + pow(dist / radius, 2.0));
        vec4 lightColor = mix(vec4(1.0, 0.8431, 0., 1.), vec4(1.0), attenuation / 2.);
        lightColor.g += 0.1 * (1.0 - attenuation);
        lightColor.b -= 0.1 * (1.0 - attenuation);
        lightColor *= attenuation * 1.2;
        render_color += lightColor;
#elif 1
        float diameter = (sin(sts[i].z * 2 + time) * 10 + 50);
        float rad = (diameter / 2.) / res.x;
        if (dist < rad) {
            render_color += vec4(0.6588, 0.5901, 0., 1.) *  (1 / dist) * 0.02;
        }
#endif
    }
    
    // for futur fire trail effect
    
    vec4 fire_col = texture(fire_tex, uv);
    if (fire_col.a > 0) {
        render_color = mix(vec4(0.), fire_col, fire_col.a);
    }
    
    // render asteroid repulsion effect
    
    if (repulse_ti > 0) {
        float radius = repulse_ti * 1000;
        vec2 pixel = uv * res;
        float d = distance(pixel, player_pos);
        if (d < radius-8.) {
            render_color.rgb = mix(render_color.rgb, mix(render_color.rgb, vec3(1., 0., 0.), (d-radius+80.) * 0.009), step(radius-80., d));
        }
    }
    
    // render player shield
    
    if (shield > 0) {
        vec2 pixel = uv * res;
        float d = distance(pixel, player_pos);
        float radius = 50;
        if (d < radius) {
            render_color.rgb = mix(render_color.rgb, mix(render_color.rgb, vec3(0., 0., 1.), (d-radius+30.) * 0.03), step(radius-40., d));
        }
    }
    
    // menu bkg grid
    
    if (menu) {
        vec2 r = mod(res * uv + mouse * 0.05, grid_size);
        vec2 lines = smoothstep(0.95, 1., r / grid_size);
        float col = dot(lines, vec2(1.));
        col *= max(1. - center_dist * 1.6, 0.);
        render_color.b += col;
        render_color.g += col * 0.5;
    }
    
    // render ui
    
    vec4 ui_col = texture(ui_surf, uv);
    if (ui_col.a > 0) {
        render_color = mix(render_color, ui_col, ui_col.a);
    }
    
    // final output
    
    f_color = render_color;
}