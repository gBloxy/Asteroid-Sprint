
import pygame

from scripts.vfx import blit_glowing_text, generate_glowing_text
from scripts.utils import increase_rect, blit_center


fp = 'asset/orbitron-bold.otf' # Font Path


class Button():
    def __init__(self, center, text, font_size=26, size=None, border=True, gaussian_power=5, align='center'):
        self.image = pygame.Surface((400, 100), pygame.SRCALPHA)
        self.image = blit_glowing_text(
            self.image, text, pygame.font.Font(fp, font_size), 'white', 'cyan', gaussian_power, center=(self.image.get_width()/2, self.image.get_height()/2))
        self.image_rect = self.image.get_rect(center=center)
        self.text_size = list(pygame.font.Font(fp, font_size).render(text, True, 'white').get_size())
        if size is None:
            size = [self.text_size[0] + 40, self.text_size[1] + 16]
        self.min_size = size[0]
        self.max_size = size[0] + 25
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.normal_rect = self.rect.copy()
        self.border = border
        self.hovered = False
        self.clicked = False
        self.border_width = 3
        self.align = align
        
    def update_state(self):
        self.clicked = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
        else:
            self.hovered = False
    
    def stop_hovered(self):
        self.hovered = False
        self.border_width = 3
        center = self.rect.center
        self.rect = self.normal_rect.copy()
        self.rect.center = center
        
    def update(self, dt):
        self.update_state()
        if self.hovered:
            if self.rect.width < self.max_size:
                increase_rect(self.rect, (2, 0))
                self.border_width += 0.08
            if self.clicked:
                return True
        else:
            if self.rect.width > self.min_size:
                increase_rect(self.rect, (-2, 0))
                self.border_width -= 0.08
        return False
    
    def render(self, surf):
        if self.align == 'center':
            blit_center(surf, self.image, self.rect.center)
        elif self.align == 'right':
            surf.blit(self.image, (self.rect.right - (self.image_rect.width - self.text_size[0])/2 - self.text_size[0] - 25, self.rect.centery - self.image_rect.height/2))
        elif self.align == 'left':
            surf.blit(self.image, (self.rect.left - self.image_rect.width/2 + self.text_size[0]/2 + 25, self.rect.centery - self.image_rect.height/2))
        if self.border:
            pygame.draw.rect(surf, 'lightblue', self.rect, round(self.border_width))


class AnimatedButton(Button):
    def __init__(self, center, text, size=None, font_size=26, align='center'):
        super().__init__(center, text, font_size=font_size, size=size, align=align)
        self.animation_timer = 450
        self.animated = False
        
    def update(self, dt):
        self.update_state()
        if self.hovered:
            if self.rect.width < self.max_size:
                increase_rect(self.rect, (2, 0))
                self.border_width += 0.08
            if self.clicked and not self.animated:
                self.animated = True
        else:
            if self.rect.width > self.min_size:
                increase_rect(self.rect, (-2, 0))
                self.border_width -= 0.08
        if self.animated:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                self.animation_timer = 450
                self.animated = False
                self.rect = self.normal_rect.copy()
                self.border_width = 3
                return True
            center = self.rect.center
            self.rect.width += 30
            self.rect.height += 30
            self.rect.center = center
        return False


class ClickableText(Button):
    def __init__(self, center, text, mode='underlined', font_size=18):
        super().__init__(center, text, font_size=font_size, border=False, gaussian_power=5)
        self.rect = pygame.Rect(0, 0, *self.text_size)
        self.rect.center = center
        self.mode = mode
    
    def update(self):
        self.update_state()
        if self.hovered and self.clicked:
                return True
        return False
    
    def render(self, surf):
        if self.hovered:
            if self.mode == 'underlined':
                super().render(surf)
                pygame.draw.rect(surf, 'lightblue', (self.rect.left, self.rect.bottom-3, self.rect.width, 2))
            elif self.mode == 'zoomed':
                blit_center(surf, pygame.transform.scale(self.image, (self.image.get_width()+15, self.image.get_height()+15)), self.image_rect.center)
        else:
            super().render(surf)


class SwitchButton():
    def __init__(self, center, text, activated=True):
        font = pygame.font.Font(fp, 18)
        rendered_text = font.render(text, True, 'black')
        size = rendered_text.get_size()
        self.text_img = generate_glowing_text((size[0]+6, size[1]+6), text, font, 'white', 'cyan', center=(size[0]/2+3, size[1]/2+3), gaussian_power=3, mode=1)
        self.img_rect = self.text_img.get_rect()
        self.rect = pygame.Rect(0, 0, 50, 25)
        self.state = activated
        self.move(center)
    
    def move(self, center):
        self.img_rect.midright = (center[0] - 5, center[1] + 2)
        self.rect.midleft = (center[0] + 5, center[1])
    
    def toggle(self):
        self.state = not self.state
    
    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                self.toggle()
                return True
        return None
    
    def render(self, surf):
        surf.blit(self.text_img, self.img_rect)
        if self.state:
            pygame.draw.circle(surf, 'green', (self.rect.right - self.rect.width/3 + 4, self.rect.centery), self.rect.height/2-2)
        else:
            pygame.draw.circle(surf, 'red', (self.rect.left + self.rect.width/3 - 3, self.rect.centery), self.rect.height/2-2)
        pygame.draw.rect(surf, 'lightblue', self.rect, 2, border_radius=75)


class Slider():
    def __init__(self, center, game, width=150, start_value=0.5, show_val=False):
        self.g = game
        self.center = center
        self.value = start_value
        self.width = width
        self.callback = None
        
        self.bar_rect = pygame.Rect(center[0] - width / 2, center[1] - 13, width, 26)
        
        self.bar_img = pygame.Surface((width + 11, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.bar_img, 'cyan', (3, 6, width+6, 6), border_radius=10)
        pygame.draw.rect(self.bar_img, 'cyan', (3, 9, width+6, 6), border_radius=10)
        self.bar_img = pygame.transform.box_blur(self.bar_img, 5)
        pygame.draw.rect(self.bar_img, 'white', (6, 8, width, 5), border_radius=10)
        
        self.cursor_rect = pygame.Rect(self.bar_rect.x + width * start_value - 4, center[1] - 13, 8, 26)
        
        self.font = pygame.font.Font(fp, 16)
        
        if show_val:
            self.text_img = self.new_text_image()
            self.text_co = (self.center[0] + width / 2 + 40, self.center[1] + 1)
        else:
            self.text_img = None
        
    def new_text_image(self):
        return self.font.render(str(round(self.value*100))+'%', True, 'lightblue')
    
    def set_value(self, value):
        self.value = value
        self.cursor_rect.x = self.bar_rect.x + self.width * self.value
        self.text_img = self.new_text_image()
    
    def set_callback(self, func):
        self.callback = func
    
    def update(self):
        if pygame.mouse.get_pressed()[0] and self.bar_rect.collidepoint(self.g.mouse_pos):
            old = self.value
            new = (self.g.mouse_pos[0] - self.bar_rect.x) / self.width
            if old != new:
                self.set_value(new)
                if self.callback is not None:
                    self.callback(self.value)
    
    def render(self, surf: pygame.Surface):
        blit_center(surf, self.bar_img, self.center)
        pygame.draw.rect(surf, 'lightblue', self.cursor_rect, border_radius=5)
        if self.text_img is not None:
            blit_center(surf, self.text_img, self.text_co)
        surf.set_at(self.center, 'black')