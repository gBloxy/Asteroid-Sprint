#version 330 core

uniform sampler2D tex;

in vec2 uv;
out vec4 frag_col;

void main() {
    frag_col = texture(tex, uv);
}