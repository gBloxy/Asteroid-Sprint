
import pygame
from math import sqrt, cos, sin, atan2, dist
from random import uniform
from time import time

import scripts.core as c


def collide_circle(rect, circle):
    testX = circle.centerx
    testY = circle.centery

    if circle.centerx < rect.x:
        testX = rect.x
    elif circle.centerx > rect.x + rect.width:
        testX = rect.x + rect.width

    if circle.centery < rect.y:
        testY = rect.y
    elif circle.centery > rect.y + rect.height:
        testY = rect.y + rect.height

    d = dist((testX, testY), circle.center)
    return d <= circle.width/2


def collide(player, a):
    if collide_circle(player.rect, a.rect):
        offset = (a.rect.x - player.rect.x, a.rect.y - player.rect.y)
        if player.mask.overlap(a.mask, offset):
            return True
    return False


class Asteroid():
    def __init__(self, pos, radius, velocity, image, motion=[0,1]):
        self.rect = pygame.FRect(0, 0, radius*2, radius*2)
        self.rect.center = pos
        self.radius = radius
        self.velocity = velocity
        self.motion = motion
        self.image = pygame.transform.scale(image, (radius*2, radius*2))
        self.angle = 0
        self.rotation = uniform(0.05, 0.3)
        mask_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surf, (255, 255, 255, 255), (radius+3, radius+3), radius-6)
        self.mask = pygame.mask.from_surface(mask_surf)
        self.force = [0, 0]
    
    def apply_force(self, force):
        self.force = force
        self.rotation *= 4
        
    def update(self, speed, rot_speed, dt):
        self.angle -= self.rotation * rot_speed
        
        vel = max(self.velocity + speed, c.MINIMUM_SPEED) * dt
        
        self.rect.x += self.motion[0] * vel
        self.rect.y += self.motion[1] * vel
        
        if any(self.force):
            self.rect.x += self.force[0] * vel
            self.rect.y += self.force[1] * vel


class Collectible():
    def __init__(self, x, y, size, velocity, game):
        self.g = game
        self.x = x
        self.y = y
        self.size = size
        self.velocity = velocity
        self.force = [0, 0]
        self.alive = True
    
    def apply_force(self, force):
        self.force = force
    
    def collect(self):
        self.alive = False
    
    def update(self, speed, magnet_power, dt):
        default_speed = max(self.velocity + speed, c.MINIMUM_SPEED) * dt
        
        if any(self.force):
            self.x += self.force[0] * default_speed
            self.y += self.force[1] * default_speed
        
        dx = self.g.player.rect.centerx - self.x
        dy = self.g.player.rect.centery - self.y
        d = sqrt(dx**2 + dy**2)
        magnet_range = 18 + magnet_power * 20
        
        if d <= magnet_range:
            attraction = magnet_power / d * 100 + magnet_power * 3
            rads = atan2(dy, dx)
            speed = max(attraction * self.g.dt/100, default_speed)
            
            self.x += cos(rads) * speed
            self.y += sin(rads) * speed
            
            if self.g.player.rect.collidepoint((self.x, self.y)):
                self.collect()
        else:
            self.y += default_speed
            
            if self.y > c.WIN_SIZE[1] + self.size or self.x > c.WIN_SIZE[0] + self.size or self.x < -self.size:
                self.alive = False


class StellarCredit(Collectible):
    def __init__(self, x, y, radius, velocity, game):
        super().__init__(x, y, 10, velocity, game)
        self.radius = radius
    
    def collect(self):
        self.g.current_credits += self.radius - 2
        self.g.score += 30
        self.alive = False
    
    def render(self, surf, offset):
        diameter = sin(self.radius * 2 + time()) * 10 + 50
        image = pygame.transform.scale(self.g.asset.glow_img, (diameter, diameter))
        c.blit_center(surf, image, (self.x + offset/2, self.y + offset/2), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(surf, 'white', (self.x + offset/2, self.y + offset/2), self.radius)


class Bonus(Collectible):
    def __init__(self, x, y, velocity, callback, img, game):
        super().__init__(x, y, img.get_width()//2, velocity, game)
        self.img = img
        self.angle = 0
        self.rotation = uniform(0.1, 0.35)
        self.callback = callback
    
    def collect(self):
        self.g.score += 40
        self.callback()
        self.alive = False
    
    def apply_force(self, force):
        self.force = force
        self.rotation *= 4
    
    def update(self, speed, magnet_power, dt):
        super().update(speed, magnet_power, dt)
        self.angle -= self.rotation
    
    def render(self, surf, offset):
        c.blit_center(surf, pygame.transform.rotate(self.img, self.angle), (self.x + offset, self.y + offset))
