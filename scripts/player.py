
import pygame
from math import sqrt, atan2, cos, sin
from time import monotonic

import scripts.core as c
from scripts.entities import collide
from scripts.vfx import Polygon


class Player():
    def __init__(self, game):
        self.g = game
        self.rect = pygame.FRect(0, 0, 52, 50)
        self.image = self.g.asset.spaceship_idle
        self.mask = pygame.mask.from_surface(self.image)
        self.collided = None
        self.ability_timer = 0
        self.repulse_time = 0
        self.repulse_delay = 0
        self.shield = 0
        self.shield_color = 'mediumblue'
    
    def crash(self):
        self.image = self.g.asset.spaceship_idle
        return self.collided
    
    def repulse(self):
        if self.ability_timer <= 0:
            for a in self.g.asteroids + self.g.bonuses + self.g.points:
                dx = (a.rect.x if hasattr(a, 'rect') else a.x) - self.rect.x
                dy = (a.rect.y if hasattr(a, 'rect') else a.y) - self.rect.y
                d = sqrt(dx**2 + dy**2)
                power = 500 / d
                angle = atan2(dy, dx)
                force = [cos(angle) * power, sin(angle) * power]
                a.apply_force(force)
            
            self.repulse_time = monotonic()
            self.ability_timer = 2000
    
    def set_shield(self, time):
        self.shield = time
    
    def update(self, dt):
        # update timers
        if self.ability_timer > 0:
            self.ability_timer -= self.g.dt # dt * 100
        
        if self.shield > 0:
            self.shield -= self.g.dt
        
        if self.repulse_time:
            self.repulse_delay = monotonic() - self.repulse_time
            if self.repulse_delay > 1:
                self.repulse_time = 0
                self.repulse_delay = 0
        
        # update animation
        pos = c.MOUSE_POS
        inclination = (pos[0] - self.rect.centerx) / 2.5
        
        if inclination < 0:
            self.image = self.g.asset.spaceship_left[min(4, int(-inclination))]
        elif inclination > 0:
            self.image = self.g.asset.spaceship_right[min(4, int(inclination))]
        else:
            self.image = self.g.asset.spaceship_idle
        
        # move
        self.rect.center = pos
        
        # check collisions with asteroids
        for a in self.g.asteroids:
            if collide(self, a):
                if self.shield <= 0:
                    self.collided = a
                    return True
                else:
                    self.shield = 0
                    self.g.asteroids.remove(a)
                    for i in range(20):
                        self.g.vfx_particles.append(Polygon(self.rect.center, color=self.shield_color))
        return False # its alive
    
    def render(self, surf, offset):
        center = (self.rect.centerx + offset, self.rect.centery + offset)
        
        if self.repulse_time:
            pygame.draw.circle(surf, 'orangered', center, self.repulse_delay * 1000, 8)
        
        c.blit_center(surf, self.image, center)
        
        if self.shield > 0:
            # shield
            pygame.draw.circle(surf, self.shield_color, center, 50, 5)
            
            # shield timer
            ext = (self.rect.left-37, self.rect.top-37, 124, 124)
            r1 = pygame.draw.arc(surf, 'blue', (self.rect.left-32, self.rect.top-32, 114, 114), c.PI_3, c.TWO_PI_3)
            r2 = pygame.draw.arc(surf, 'blue', ext, c.PI_3, c.TWO_PI_3)
            pygame.draw.line(surf, self.shield_color, r1.bottomright, r2.bottomright)
            pygame.draw.line(surf, self.shield_color, r1.bottomleft,  r2.bottomleft)
            val = self.shield / c.SHIELD_DURATION
            pygame.draw.arc(surf, 'lightgreen', ext, c.TWO_PI_3 - val * c.PI_3, c.TWO_PI_3, 5)
