
from random import randint, choice
from math import cos, sin, radians
import pygame
from pygame.math import Vector2



# FIRE COLORS -----------------------------------------------------------------

palette = ((255, 255, 0 ),
           (255, 173, 51),
           (247, 117, 33),
           (191, 74 , 46),
           (115, 61 , 56),
           (61 , 38 , 48))[::-1] # reverse the color order


# DEATH EFFECT ----------------------------------------------------------------

class GeometricObject():
    alpha = 255
    color = (255, 255, 255, alpha)
    def __init__(self, center):
        self.points = [[], [], [], []]
        self.center = list(center)
        self.angle = randint(-180, 180)
        self.perpendicular_straight = randint(2, 3)
        self.alive = True
        self.dir = None
        self.speed = randint(5, 9) # customized
        self.decay_factor = 0.07
        self.delta = 0.008 * 25
    
    def create_polygon(self):
        x = self.center[0] + self.length * cos(radians(self.angle))
        y = self.center[1] + self.length * sin(radians(self.angle))
        self.points[0] = Vector2([x, y])
        x = self.center[0] - self.length * cos(radians(self.angle))
        y = self.center[1] - self.length * sin(radians(self.angle))
        self.points[1] = Vector2([x, y])
        x1, x2 = self.points[0][0], self.points[1][0]
        y1, y2 = self.points[0][1], self.points[1][1]
        x3, y3 = self.center
        B = Vector2(y1 - y2, x2 - x1)
        B.normalize_ip()
        x, y = Vector2(x3, y3) + self.perpendicular_straight * B
        self.points[2] = Vector2([x, y])
        x, y = Vector2(x3, y3) - self.perpendicular_straight * B
        self.points[3] = Vector2([x, y])
        self.points[1], self.points[2] = self.points[2], self.points[1]
    
    def calculate_direction(self):
        self.dir = pygame.math.Vector2(self.points[2] - self.points[0])
        self.dir.normalize_ip()
        self.dir.scale_to_length(self.speed)
    
    def new_points(self, factor):
        self.points[0] = self.points[0] + (self.points[2] - self.points[0]) * factor
        self.points[1] = self.points[1] + (self.points[2] - self.points[1]) * factor
        self.points[3] = self.points[3] + (self.points[2] - self.points[3]) * factor
        
    def rotate(self, angle):
        for vector in self.points:
            vector.rotate_ip(angle)
    
    def update_position(self):
        for point in range(len(self.points)):
            for i in range(2):
                self.points[point][i] += self.dir[i] * self.delta
    
    def update_speed(self):
        self.speed -= self.deceleration
        if self.speed <= 0:
            self.alive = False
    
    def update(self, dt):
        self.new_points(self.decay_factor)
        self.update_position()
        self.update_speed()
        self.calculate_direction()
    
    def render(self, surface):
        if self.alive:
            pygame.draw.polygon(surface, self.color, self.points, width=0)


class Line(GeometricObject):
    def __init__(self, center):
        super().__init__(center)
        self.length = randint(75, 100)*5  # customized
        self.create_polygon()
        self.factor = choice([-1, 1])
        self.calculate_direction()
        self.deceleration = 0.03
    
    def calculate_direction(self):
        super().calculate_direction()
        self.dir = self.dir * self.factor
    
    def update_decay_factor(self):
        self.decay_factor -= 0.008


class Polygon(GeometricObject):
    def __init__(self, center):
        super().__init__(center)
        self.length = randint(5, 30)*6  # customized
        self.create_polygon()
        self.factor = choice([-1, 1])
        self.calculate_direction()
        self.deceleration = 0.04
    
    def update_decay_factor(self):
        self.decay_factor -= 0.00008
    
    def update(self, dt):
        super().update(dt)
        self.update_decay_factor()


# FIRE EFFECT -----------------------------------------------------------------

class FireParticle():
    def __init__(self, x, y, size):
        self.x, self.y = x, y
        self.maxlife = randint(13 + int(size*5), 27 + int(size*10))
        self.life = self.maxlife
        self.dir = choice((-2, -1, 1, 2))
        self.sin = randint(-10, 10)/7
        self.sinr = randint(5, 10)
        self.r = randint(0,2)
        self.ox = randint(-1, 1)
        self.oy = randint(-1, 1)


class Fire():
    size = 3.2
    density = 4.2
    rise = 5
    spread = 1.2
    wind = 0
    res = 2
    def __init__(self, game):
        self.g = game
        self.particles = list()
        self.dead = list()
        self.j = 0
        self.x, self.y = game.mouse_pos
        self.bsurf = pygame.Surface((game.WIN_SIZE[0]//self.res,game.WIN_SIZE[1]//self.res),
                                    pygame.SRCALPHA).convert_alpha()
        self.alive = True
    
    def update_render(self, surf, dt):
        self.x = self.g.player.rect.centerx
        self.y = self.g.player.rect.bottom
        
        self.bsurf.fill((0, 0, 0, 0))
        
        self.j += 1
        if self.j > 360:
            self.j = 0
        
        if self.alive:
            for _ in range(round(self.density)):
                self.particles.append(FireParticle(self.x//self.res, self.y//self.res, self.size))
        
            pygame.draw.circle(self.bsurf, palette[5], (self.x//self.res, self.y//self.res-2), 2, 0)
        
        for p in self.particles:
            p.life -= 1
            if p.life == 0:
                self.dead.append(p)
                continue
            
            i = int((p.life/p.maxlife)*6)
            
            p.y += self.rise
            p.x += ((p.sin * sin(self.j/(p.sinr)))/2) * self.spread + self.wind
            
            if not randint(0, 5):
                p.r += 0.88
                
            x, y = p.x, p.y
            
            x += p.ox*(5-i)
            y += p.oy*(5-i)
            
            alpha = 255
            if p.life < p.maxlife/4:
                alpha = int((p.life/p.maxlife)*255)
            
            pygame.draw.circle(self.bsurf, palette[i] + (alpha,), (x, y), p.r, 0)
            
            if i == 0:
                pygame.draw.circle(self.bsurf, (0, 0, 0, 0), (x+randint(-1, 1), y-4), p.r*(((p.maxlife-p.life)/p.maxlife)/0.88), 0)
            else:
                pygame.draw.circle(self.bsurf, palette[i-1] + (alpha,), (x+randint(-1, 1), y-3), p.r/1.5, 0)
        
        for p in self.dead:
            self.particles.remove(p)
        self.dead.clear()
        
        surf.blit(pygame.transform.scale(self.bsurf, (surf.get_width(), surf.get_height())), (0, 0))
