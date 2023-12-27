
import pygame
from math import sqrt
from os import listdir
from random import uniform


def blit_center(surface, surf, center):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2))


def lerp(a, b, t):
    return a + t * (b - a)


def load_images(path):
    images = []
    for name in listdir(path):
        if name.endswith('.png'):
            surf = pygame.image.load(path+name).convert()
            surf.set_colorkey('white')
            images.append(surf)
    return images


def collide(rect, circle):
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

    distX = circle.centerx - testX
    distY = circle.centery - testY
    distance = sqrt((distX * distX) + (distY * distY))

    return distance <= circle.width/2


spaceship_image = pygame.image.load('asset\\spaceship.png')
spaceship_image.set_colorkey('black')
spaceship_crashed_image = pygame.image.load('asset\\spaceship_crashed.png')
spaceship_crashed_image.set_colorkey('black')


class Player():
    def __init__(self, x, y, game):
        self.g = game
        self.rect = pygame.FRect(0, 0, 20, 40)
        self.rect.center = (x, y)
        self.velocity = 15 # To implement later
        self.image = spaceship_image
    
    def crash(self):
        self.image = spaceship_crashed_image
        
    def update(self, dt):
        self.rect.center = self.g.mouse_pos
        for a in self.g.asteroids:
            if collide(self.rect, a.rect):
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
        
    def update(self, speed, dt):
        self.angle -= self.rotation
        self.rect.x += self.motion[0] * (speed + self.velocity) * dt
        self.rect.y += self.motion[1] * (speed + self.velocity) * dt
