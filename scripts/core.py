
from os import listdir
from json import dump, load
import pygame


WIN_SIZE = [525, 650]
MAX_STELLAR_CREDITS = 5

CLICK = False
MOUSE_POS = (0, 0)

ITCH_URL = 'https://g-bloxy.itch.io/asteroid-sprint'
GITHUB_URL = 'https://github.com/gBloxy/Asteroid-Sprint'

fp = 'asset/orbitron-bold.otf' # Font Path


def blit_center(surface, surf, center, *args, **kwargs):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2), *args, **kwargs)


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
        data = load(file)
    return data


def write_file(file_path, data):
    with open(file_path, 'w') as file:
        dump(data, file)


def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds


def line_wrapp(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = 5
    fontHeight = font.size("Tg")[1]
    
    while text:
        i = 1
        if y + fontHeight > rect.bottom:
            break
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
        text = text[i:]
