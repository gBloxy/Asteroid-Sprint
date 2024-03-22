
import pygame
from math import sqrt, cos, sin, atan2, dist
from random import uniform
from time import time
from os import listdir

from scripts.core import blit_center


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


def load_images():
    global glow_img, light_img, spaceship_idle, spaceship_right, spaceship_left
    glow_img = pygame.Surface((255, 255))
    glow_img.fill((240 * 0.7, 215 * 0.7, 0))
    light_img = pygame.image.load('asset\\light.png')
    light_img.set_colorkey((0, 0, 0))
    glow_img.blit(light_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    spaceship_idle = pygame.image.load('asset\\spaceship\\idle.png')
    spaceship_idle.convert_alpha()
    
    spaceship_right = [pygame.image.load('asset\\spaceship\\right\\'+name) for name in listdir('asset\\spaceship\\right\\')]
    for s in spaceship_right:
        s.convert_alpha()
    spaceship_left = [pygame.image.load('asset\\spaceship\\left\\'+name) for name in listdir('asset\\spaceship\\left\\')]
    for s in spaceship_left:
        s.convert_alpha()


class Player():
    def __init__(self, x, y, game):
        self.g = game
        self.rect = pygame.FRect(0, 0, 52, 50)
        self.rect.center = (x, y)
        self.velocity = 15 # To implement later
        self.image = spaceship_idle
        self.mask = pygame.mask.from_surface(self.image)
    
    def crash(self):
        self.image = spaceship_idle
        
    def update(self, dt):
        pos = self.g.mouse_pos
        inclination = (pos[0] - self.rect.centerx) / 2.5
        
        if inclination < 0:
            self.image = spaceship_left[min(4, int(-inclination))]
        elif inclination > 0:
            self.image = spaceship_right[min(4, int(inclination))]
        else:
            self.image = spaceship_idle
        
        self.rect.center = pos
        for a in self.g.asteroids:
            if collide(self, a):
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
        
    def update(self, speed, dt):
        self.angle -= self.rotation
        self.rect.x += self.motion[0] * (speed + self.velocity) * dt
        self.rect.y += self.motion[1] * (speed + self.velocity) * dt


class StellarCredit():
    def __init__(self, x, y, radius, velocity, game):
        self.g = game
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = velocity
        self.alive = True
    
    def update(self):
        dx = self.g.player.rect.centerx - self.x
        dy = self.g.player.rect.centery - self.y
        d = sqrt(dx**2 + dy**2)
        magnet_range = 18 + self.g.magnet_power * 20
        default_speed = (self.velocity + self.g.speed) * self.g.dt/100
        
        if d <= magnet_range:
            attraction = self.g.magnet_power / d * 100 + self.g.magnet_power * 3
            rads = atan2(dy, dx)
            speed = max(attraction * self.g.dt/100, default_speed)
            
            self.x += cos(rads) * speed
            self.y += sin(rads) * speed
            
            if self.g.player.rect.collidepoint((self.x, self.y)):
                self.alive = False
                return True
        else:
            self.y += default_speed
            if self.y > self.g.WIN_SIZE[1] + 10:
                self.alive = False
        return False
    
    def render(self, surf, offset):
        diameter = sin(self.radius * 2 + time()) * 10 + 50
        image = pygame.transform.scale(glow_img, (diameter, diameter))
        blit_center(surf, image, (self.x + offset/2, self.y + offset/2), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(surf, 'white', (self.x + offset/2, self.y + offset/2), self.radius)
