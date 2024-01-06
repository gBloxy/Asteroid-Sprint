
import pygame
from array import array
import moderngl


class ShaderWindow():
    def __init__(self, size, caption, shader_path):
        self.WIN_SIZE = size
        self.window = pygame.display.set_mode(self.WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption(caption)
        self.ctx = moderngl.create_context()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 1.0,                            ]))
        self.shader_path = shader_path
        vert_shader = self.load_shader_file('shader.vert')
        frag_shader = self.load_shader_file('shader.frag')
        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])
        self.index = 1
    
    def get_index(self):
        i = self.index
        self.index += 1
        return i
    
    def load_shader_file(self, name):
        with open(self.shader_path+name, 'r') as file:
            data = file.read()
        return data
    
    def load_const_surface(self, name, surf):
        tex = self.surf_to_texture(surf)
        index = self.get_index()
        tex.use(index)
        self.program[name] = index
    
    def load_const_var(self, name, const):
        self.program[name] = const
    
    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex
    
    def render(self, display, surfaces={}, **kwargs):
        self.frame_tex = self.surf_to_texture(display)
        self.frame_tex.use(0)
        self.program['tex'] = 0
        
        index = self.index
        textures = []
        for surf_name in surfaces:
            surf = self.surf_to_texture(surfaces[surf_name])
            surf.use(index)
            self.program[surf_name] = index
            textures.append(surf)
            index += 1
        
        for var in kwargs:
            self.program[var] = kwargs[var]
        
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        
        for tex in textures + [self.frame_tex]:
            tex.release()
