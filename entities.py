
import pygame
from math import sqrt


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

    return distance <= circle.width


class Player():
    def __init__(self, x, y, game):
        self.g = game
        self.rect = pygame.FRect(0, 0, 20, 40)
        self.rect.center = (x, y)
        self.velocity = 15 # To implement later
        
    def update(self, dt):
        self.rect.center = self.g.mouse_pos
        for a in self.g.asteroids:
            if collide(self.rect, a.rect):
                return True
        return False


class Asteroid():
    def __init__(self, pos, radius, velocity, color, motion=[0,1]):
        self.rect = pygame.FRect(0, 0, radius, radius)
        self.rect.center = pos
        self.radius = radius
        self.velocity = velocity
        self.motion = motion
        self.color = color
        
    def update(self, speed, dt):
        self.rect.x += self.motion[0] * (speed + self.velocity) * dt
        self.rect.y += self.motion[1] * (speed + self.velocity) * dt
