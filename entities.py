
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


def collide_line(line_start, line_end, rect):
    if rect.collidepoint(line_start) or rect.collidepoint(line_end):
        return True
    
    rect_left = rect.left
    rect_right = rect.right
    rect_top = rect.top
    rect_bottom = rect.bottom

    if line_intersects((rect_left, rect_top), (rect_left, rect_bottom), line_start, line_end):
        return True
    if line_intersects((rect_right, rect_top), (rect_right, rect_bottom), line_start, line_end):
        return True
    if line_intersects((rect_left, rect_top), (rect_right, rect_top), line_start, line_end):
        return True
    if line_intersects((rect_left, rect_bottom), (rect_right, rect_bottom), line_start, line_end):
        return True

    return False


def line_intersects(line1_start, line1_end, line2_start, line2_end):
    x1, y1 = line1_start
    x2, y2 = line1_end
    x3, y3 = line2_start
    x4, y4 = line2_end

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        return False  # Lines are parallel

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

    if (min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2) and
            min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4)):
        return True

    return False


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


class Laser():
    def __init__(self, x, end):
        self.x = x
        self.end = end
        self.timer = 0
    
    def current(self):
        return lerp(self.x, self.end, self.timer/1000)
