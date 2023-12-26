
import pygame

from vfx import blit_glowing_text
from entities import blit_center


fp = 'asset/conthrax-sb.otf' # Font Path


class Button():
    def __init__(self, center, text, size=40, border=True, gaussian_power=10):
        self.image = pygame.Surface((400, 100), pygame.SRCALPHA)
        self.image = blit_glowing_text(self.image, (self.image.get_width()/2, self.image.get_height()/2), text, pygame.font.Font(fp, size), 'white', 'cyan', gaussian_power)
        self.image_rect = self.image.get_rect(center=center)
        size = list(pygame.font.Font(fp, size).render(text, True, 'white').get_size())
        self.text_size = size
        size = [size[0] + 40, size[1] + 10]
        self.min_size = size[0]
        self.max_size = size[0] + 20
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.normal_rect = self.rect.copy()
        self.border = border
        
    def update(self, dt, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.rect.width < self.max_size:
                center = self.rect.center
                self.rect.width += 1
                self.rect.center = center
            if pygame.mouse.get_pressed()[0]:
                return True
        else:
            if self.rect.width > self.min_size:
                center = self.rect.center
                self.rect.width -= 1
                self.rect.center = center
        return False
    
    def render(self, surf, offset_x=0):
        surf.blit(self.image, (self.image_rect.x + offset_x, self.image_rect.y))
        if self.border:
            pygame.draw.rect(surf, 'lightblue', (self.rect.x + offset_x, self.rect.y, self.rect.width, self.rect.height), 3)


class AnimatedButton(Button):
    def __init__(self, center, text):
        super().__init__(center, text)
        self.animation_timer = 450
        self.animated = False
        
    def update(self, dt, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.rect.width < self.max_size:
                center = self.rect.center
                self.rect.width += 1
                self.rect.center = center
            if pygame.mouse.get_pressed()[0] and not self.animated:
                self.animated = True
        else:
            if self.rect.width > self.min_size:
                center = self.rect.center
                self.rect.width -= 1
                self.rect.center = center
        if self.animated:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                self.animation_timer = 450
                self.animated = False
                self.rect = self.normal_rect.copy()
                return True
            center = self.rect.center
            self.rect.width += 30
            self.rect.height += 30
            self.rect.center = center
        return False


class ClickableText(Button):
    def __init__(self, center, text, mode='underlined'):
        super().__init__(center, text, size=15, border=False, gaussian_power=5)
        self.hovered = False
        self.rect = pygame.Rect(0, 0, *self.text_size)
        self.rect.center = center
        self.mode = mode
    
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                return True
        else:
            self.hovered = False
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


class Menu():
    def __init__(self, game):
        self.g = game
        self.image = self.create_main_image(game)
        self.credits_image, self.credits_rect = self.create_credits_page(game)
        self.setup_buttons(game)
        self.credits_anim = False
        self.credits_anim_sens = -1
        self.credits_active = False
        self.offset_x = 0
        
    def create_main_image(self, game):
        image = pygame.Surface(game.WIN_SIZE, pygame.SRCALPHA)
        image = blit_glowing_text(image, (game.WIN_SIZE[0]/2, 75), 'ASTEROID', pygame.font.Font(fp, 60), 'white', 'cyan')
        image = blit_glowing_text(image, (game.WIN_SIZE[0]/2, 150), 'SPRINT', pygame.font.Font(fp, 60), 'white', 'cyan')
        image = blit_glowing_text(image, (165, game.WIN_SIZE[1]-25), 'sound on/off : press [m]', pygame.font.Font(fp, 15), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (game.WIN_SIZE[0]/2, 525), 'press [ECHAP] to quit', pygame.font.Font(fp, 15), 'white', 'cyan', 3)
        return image
    
    def setup_buttons(self, game):
        self.play_button = AnimatedButton((game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2), 'Play')
        self.quit_button = Button((game.WIN_SIZE[0]/2, 420), 'Quit')
        self.credits_button = ClickableText((game.WIN_SIZE[0]-50, game.WIN_SIZE[1]-25), 'credits')
        self.credits_close_button = ClickableText((self.credits_rect.right - 27, self.credits_rect.top + 27), 'X', mode='zoomed')
        
    def create_credits_page(self, game):
        image = pygame.Surface((360, 190), pygame.SRCALPHA)
        pygame.draw.rect(image, 'cyan', (5, 5, image.get_width()-10, image.get_height()-10), 4)
        pygame.draw.rect(image, 'cyan', (10, 10, image.get_width()-20, image.get_height()-20), 4)
        image = pygame.transform.gaussian_blur(image, 4)
        pygame.draw.rect(image, 'white', (9, 9, image.get_width()-18, image.get_height()-18), 2)
        rect = image.get_rect(center=(game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 + 50))
        image = blit_glowing_text(image, (157, 27), 'INFORMATION AND CREDITS', pygame.font.Font(fp, 15), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (147, 60), 'This game was created by g_Bloxy.', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (161, 75), 'The spaceship fire trail is a customized', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (158, 90), 'version of the fire vfx of @kadir014 on', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (44, 105), 'github', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (78, 135), 'github: @gBloxy', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        image = blit_glowing_text(image, (96, 154), 'Font used: conthrax', pygame.font.Font(fp, 11), 'white', 'cyan', 3)
        return image, rect
        
    def update(self):
        if not self.credits_active:
            if self.play_button.update(self.g.dt, self.g.mouse_pos):
                self.g.start_game()
            if self.quit_button.update(self.g.dt, self.g.mouse_pos):
                self.g.quit()
        if self.credits_button.update(self.g.mouse_pos):
            if not self.credits_active and not self.credits_anim:
                self.credits_anim = True
                self.credits_anim_sens = 1
        if self.credits_active:
            if self.credits_close_button.update(self.g.mouse_pos):
                self.credits_anim = True
                self.credits_anim_sens = -1
        if self.credits_anim:
            self.offset_x += self.credits_anim_sens * 30
            if self.credits_anim_sens > 0:
                if -self.credits_rect.right + self.offset_x > self.credits_rect.x:
                    self.credits_anim = False
                    self.credits_active = True
                    self.credits_anim_sens = -1
            else:
                if self.offset_x <= 0:
                    self.credits_anim = False
                    self.credits_active = False
                    self.credits_anim_sens = 1
                    self.offset_x = 0
        
    def render(self, surf):
        surf.blit(self.image, (0, 0))
        self.play_button.render(surf, self.offset_x)
        self.quit_button.render(surf, self.offset_x)
        self.credits_button.render(surf)
        if self.credits_anim:
            surf.blit(self.credits_image, (-self.credits_rect.right + self.offset_x, self.credits_rect.y))
        elif self.credits_active:
            surf.blit(self.credits_image, self.credits_rect)
            self.credits_close_button.render(surf)
