
from os import listdir
import pygame


def blit_center(surface, surf, center):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2))


def lerp(a, b, t):
    return a + t * (b - a)


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
        data = file.read()
    return data


def write_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)


def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds
