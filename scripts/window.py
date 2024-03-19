
import pygame
from array import array
import moderngl


class ShaderWindow():
    def __init__(self, size, caption, shader_path):
        self.WIN_SIZE = size
        self.window = pygame.display.set_mode(self.WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption(caption)
        self.ctx = moderngl.create_context()
        self.vbo = self.ctx.buffer(data=array('f', [ # vertex buffer object
            -1.0, 1.0, 0.0, 0.0,  # topleft
            1.0, 1.0, 1.0, 0.0,   # topright
            -1.0, -1.0, 0.0, 1.0, # bottomleft
            1.0, -1.0, 1.0, 1.0,  # bottomright
            ]))
        self.shader_path = shader_path
        vert_shader = self.load_shader_file('shader.vert')
        frag_shader = self.load_shader_file('shader.frag')
        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '2f 2f', 'vert', 'texcoord')]) # vertex array object
        self.index = 0
        self.time = 0
    
    def get_size(self):
        return self.WIN_SIZE
    
    def get_index(self):
        i = self.index
        self.index += 1
        return i
    
    def load_shader_file(self, name):
        with open(self.shader_path+name, 'r') as file:
            data = file.read()
        return data
    
    def load_const_surface(self, name, surf, comp=4):
        tex = self.surf_to_texture(surf, comp=comp)
        index = self.get_index()
        tex.use(index)
        try:
            self.program[name] = index
        except Exception as const_error:
            print(const_error)
    
    def load_const_var(self, name, const):
        try:
            self.program[name] = const
        except Exception as const_error:
            print(const_error)
    
    def surf_to_texture(self, surf, comp=4):
        tex = self.ctx.texture(surf.get_size(), comp)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex
    
    def update(self, dt, **variables):
        self.time += dt/1000
        variables['time'] = self.time
        for var in variables:
            try:
                self.program[var] = variables[var]
            except Exception as uniform_error:
                print(uniform_error)
    
    def render(self, **surfaces):
        index = self.index
        textures = []
        
        for surf_name in surfaces:
            tex = self.surf_to_texture(surfaces[surf_name])
            tex.use(index)
            self.program[surf_name] = index
            textures.append(tex)
            index += 1
        
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        
        for tex in textures:
            tex.release()
