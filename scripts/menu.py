
import pygame

from scripts.vfx import blit_glowing_text, generate_glowing_text
from scripts.utils import increase_rect, blit_center


fp = 'asset/conthrax-sb.otf' # Font Path


class Button():
    def __init__(self, center, text, font_size=40, size=None, border=True, gaussian_power=10):
        self.image = pygame.Surface((400, 100), pygame.SRCALPHA)
        self.image = blit_glowing_text(
            self.image, text, pygame.font.Font(fp, font_size), 'white', 'cyan', gaussian_power, center=(self.image.get_width()/2, self.image.get_height()/2))
        self.image_rect = self.image.get_rect(center=center)
        self.text_size = list(pygame.font.Font(fp, font_size).render(text, True, 'white').get_size())
        if size is None:
            size = [self.text_size[0] + 40, self.text_size[1] + 16]
        self.min_size = size[0]
        self.max_size = size[0] + 20
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.normal_rect = self.rect.copy()
        self.border = border
        self.hovered = False
        self.clicked = False
        
    def update_state(self):
        self.clicked = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
        else:
            self.hovered = False
        
    def update(self, dt):
        self.update_state()
        if self.hovered:
            if self.rect.width < self.max_size:
                increase_rect(self.rect, (1, 0))
            if self.clicked:
                return True
        else:
            if self.rect.width > self.min_size:
                increase_rect(self.rect, (-1, 0))
        return False
    
    def render(self, surf, offset_x=0):
        surf.blit(self.image, (self.image_rect.x + offset_x, self.image_rect.y))
        if self.border:
            pygame.draw.rect(surf, 'lightblue', (self.rect.x + offset_x, self.rect.y - 3, self.rect.width, self.rect.height), 3)


class AnimatedButton(Button):
    def __init__(self, center, text, size=None):
        super().__init__(center, text, size=size)
        self.animation_timer = 450
        self.animated = False
        
    def update(self, dt):
        self.update_state()
        if self.hovered:
            if self.rect.width < self.max_size:
                increase_rect(self.rect, (1, 0))
            if self.clicked and not self.animated:
                self.animated = True
        else:
            if self.rect.width > self.min_size:
                increase_rect(self.rect, (-1, 0))
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
        super().__init__(center, text, font_size=18, border=False, gaussian_power=5)
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
        self.set_best_score(game.best_score)
        
    def create_main_image(self, game):
        image = pygame.Surface(game.WIN_SIZE, pygame.SRCALPHA)
        image = blit_glowing_text(image, 'ASTEROID', pygame.font.Font(fp, 63), 'white', 'cyan', center=(game.WIN_SIZE[0]/2, 90))
        image = blit_glowing_text(image, 'SPRINT', pygame.font.Font(fp, 63), 'white', 'cyan', center=(game.WIN_SIZE[0]/2, 160))
        image = blit_glowing_text(image, 'sound on/off : press [m]', pygame.font.Font(fp, 18), 'white', 'cyan', 3, center=(170, game.WIN_SIZE[1]-25))
        image = blit_glowing_text(image, 'press [ECHAP] to quit', pygame.font.Font(fp, 18), 'white', 'cyan', 3, center=(game.WIN_SIZE[0]/2, 550))
        return image
    
    def setup_buttons(self, game):
        self.play_button = AnimatedButton((game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 - 40), 'Play', size=[152, 62])
        self.quit_button = Button((game.WIN_SIZE[0]/2, 380), 'Quit', size=[152, 62])
        self.credits_button = ClickableText((game.WIN_SIZE[0]-55, game.WIN_SIZE[1]-25), 'credits')
        self.credits_close_button = ClickableText((self.credits_rect.right - 27, self.credits_rect.top + 27), 'X', mode='zoomed')
        
    def create_credits_page(self, game):
        image = pygame.Surface((400, 230), pygame.SRCALPHA)
        pygame.draw.rect(image, 'cyan', (5, 5, image.get_width()-10, image.get_height()-10), 4)
        pygame.draw.rect(image, 'cyan', (10, 10, image.get_width()-20, image.get_height()-20), 4)
        image = pygame.transform.gaussian_blur(image, 4)
        pygame.draw.rect(image, 'white', (9, 9, image.get_width()-18, image.get_height()-18), 2)
        rect = image.get_rect(center=(game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 + 30))
        font = pygame.font.Font(fp, 12)
        image = blit_glowing_text(image, 'INFORMATION AND CREDITS', pygame.font.Font(fp, 17), 'white', 'cyan', 3, topleft=(20, 22))
        image = blit_glowing_text(image, 'This game was created by g_Bloxy.', font, 'white', 'cyan', 3, topleft=(20, 54))
        image = blit_glowing_text(image, 'The spaceship fire trail is a customized version', font, 'white', 'cyan', 3, topleft=(20, 81))
        image = blit_glowing_text(image, 'of the fire vfx of @kadir014 on github.', font, 'white', 'cyan', 3, topleft=(20, 96))
        image = blit_glowing_text(image, 'The death particles are a customized version', font, 'white', 'cyan', 3, topleft=(20, 123))
        image = blit_glowing_text(image, 'of the vfx of @eliczi on github.', font, 'white', 'cyan', 3, topleft=(20, 138))
        image = blit_glowing_text(image, 'github : @gBloxy.', font, 'white', 'cyan', 3, topleft=(20, 164))
        image = blit_glowing_text(image, 'Font used : orbitron from the league of moveable type.', font, 'white', 'cyan', 3, topleft=(20, 180))
        image = blit_glowing_text(image, 'Music used : screen saver from Kevin MacLeod.', font, 'white', 'cyan', 3, topleft=(20, 196))
        return image, rect
    
    def set_best_score(self, score):
        self.best_score_img = generate_glowing_text(
            self.g.WIN_SIZE, 'best score : '+score, pygame.font.Font(fp, 25), 'white', 'cyan', 4, center=(self.g.WIN_SIZE[0]/2, 475), mode=1)
        
    def update(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if not self.credits_active:
            if self.play_button.update(self.g.dt):
                self.g.start_game()
            if self.quit_button.update(self.g.dt):
                self.g.quit()
        if self.credits_button.update():
            if not self.credits_active and not self.credits_anim:
                self.credits_anim = True
                self.credits_anim_sens = 1
        if self.credits_active:
            if self.credits_close_button.update():
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
        else:
            surf.blit(self.best_score_img, (0, 0))
