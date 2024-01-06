
from os import listdir
from json import dump, load
from math import sqrt
import pygame


def blit_center(surface, surf, center, *args, **kwargs):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2), *args, **kwargs)


def lerp(a, b, t):
    return a + t * (b - a)


def distance(pos1, pos2):
    return sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def load_image_folder(path):
    images = []
    for name in listdir(path):
        if name.endswith('.png'):
            surf = pygame.image.load(path+name).convert()
            surf.set_colorkey('white')
            images.append(surf)
    return images


def increase_rect(rect, size):
    center = rect.center
    rect.inflate_ip(*size)
    rect.center = center


def read_file(file_path):
    with open(file_path, 'r') as file:
        data = load(file)
    return data


def write_file(file_path, data):
    with open(file_path, 'w') as file:
        dump(data, file)


def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds
