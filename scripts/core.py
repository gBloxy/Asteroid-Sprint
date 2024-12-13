
from json import dump, load
from math import pi
import pygame


WIN_SIZE = [525, 650]

DEBUG = True

MAX_STELLAR_CREDITS = 5
MAGNET_DURATION = 7000
FREEZE_DURATION = 2000
SHIELD_DURATION = 5000
STARS_PROB = 1/15
BONUSES_PROB = 1/700
MINIMUM_SPEED = 3
SCORE_DELAY = 1
POWER_DELAY = 3000

PI_2 = pi / 2
PI_3 = pi / 3
TWO_PI = pi * 2
TWO_PI_3 = 2 * PI_3


CLICK = False
MOUSE_POS = (0, 0)

ITCH_URL = 'https://g-bloxy.itch.io/asteroid-sprint'
GITHUB_URL = 'https://github.com/gBloxy/Asteroid-Sprint'

fp = 'asset/orbitron-bold.otf' # Font Path


def blit_center(surface, surf, center, *args, **kwargs):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2), *args, **kwargs)


def lerp(a, b, t):
    return a + t * (b - a)


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


def line_wrapp(surface, text, color, rect, font, aa=True, bkg=None):
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


def swap_color(surf, old, new):
    pixels = pygame.surfarray.pixels3d(surf)
    old_col = pygame.Color(old)
    mask = (pixels == (old_col.r, old_col.g, old_col.b)).all(axis=-1)
    new_col = pygame.Color(new)
    pixels[mask] = (new_col.r, new_col.g, new_col.b)
    return surf
