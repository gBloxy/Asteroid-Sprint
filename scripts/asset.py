
import pygame
from os import listdir


class Asset():
    def load_image_folder(self, path):
        images = []
        for name in listdir(path):
            if name.endswith('.png'):
                surf = pygame.image.load(path+name).convert()
                surf.set_colorkey('white')
                images.append(surf)
        return images
    
    def load(self, path) -> pygame.Surface:
        return pygame.image.load('asset/'+path)
    
    def load_assets(self):
        self.icon_success = pygame.transform.scale(self.load('success/unlocked.png'), (56, 56))
        
        self.logo = self.load('ui/logo.png')
        self.upgrade_bar = self.load('ui/upgrade_bar.png').convert_alpha()
        self.upgrade_cell = self.load('ui/upgrade_cell.png').convert_alpha()
        self.container_bar = self.load('ui/container_bar.png').convert_alpha()
        self.container_cell = self.load('ui/container_cell.png').convert_alpha()
        
        self.button = self.load('ui/button.png').convert_alpha()
        self.button_hovered = self.load('ui/button_hovered.png').convert_alpha()
        self.button_clicked = self.load('ui/button_clicked.png').convert_alpha()
        
        self.noise = self.load('perlin_noise.png').convert()
        
        self.glow_img = pygame.Surface((255, 255))
        self.glow_img.fill((240 * 0.7, 215 * 0.7, 0))
        self.light_img = self.load('light.png')
        self.light_img.set_colorkey((0, 0, 0))
        self.glow_img.blit(self.light_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.asteroids = self.load_image_folder('asset/asteroids/')
        
        self.spaceship_idle  =  self.load('spaceship/idle.png').convert_alpha()
        self.spaceship_right = [self.load('spaceship/right/'+name).convert_alpha() for name in listdir('asset/spaceship/right/')]
        self.spaceship_left  = [self.load('spaceship/left/'+name).convert_alpha() for name in listdir('asset/spaceship/left/')]
        
        self.shield = self.load('power_ups/shield.png').convert_alpha()
        self.magnet = self.load('power_ups/magnet.png').convert_alpha()
