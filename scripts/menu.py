
import pygame

from scripts.vfx import blit_glowing_text, generate_glowing_text
from scripts.utils import increase_rect, blit_center


fp = 'asset/conthrax-sb.otf' # Font Path


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


class CreditPage():
    def __init__(self, game):
        self.g = game
        self.image, self.rect = self.create_credits_page(game)
        self.active = False
        self.close_button = ClickableText((self.rect.right - 27, self.rect.top + 27), 'X', mode='zoomed')
        self.pushing = False
        self.retracting = False
    
    def create_credits_page(self, game):
        image = pygame.Surface((400, 230), pygame.SRCALPHA)
        pygame.draw.rect(image, 'cyan', (5, 5, image.get_width()-10, image.get_height()-10), 4)
        pygame.draw.rect(image, 'cyan', (10, 10, image.get_width()-20, image.get_height()-20), 4)
        image = pygame.transform.gaussian_blur(image, 4)
        pygame.draw.rect(image, 'white', (9, 9, image.get_width()-18, image.get_height()-18), 2)
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
        rect = image.get_rect(center=(game.WIN_SIZE[0]/2, game.WIN_SIZE[1] + 200))
        return image, rect
    
    def process_pushing(self):
        vel = 30
        if self.rect.centery != self.g.WIN_SIZE[1]/2 + 75:
            self.rect.y -= vel
            self.close_button.rect.y -= vel
            self.close_button.image_rect.y -= vel
        else:
            self.pushing = False
            self.active = True
    
    def process_retracting(self):
        vel = 30
        if self.rect.centery != self.g.WIN_SIZE[1] + 200:
            self.rect.y += vel
            self.close_button.rect.y += vel
            self.close_button.image_rect.y += vel
        else:
            self.retracting = False
    
    def activated(self):
        return self.active or self.pushing or self.retracting
    
    def update(self):
        if self.pushing:
            self.process_pushing()
        elif self.retracting:
            self.process_retracting()
        if self.close_button.update():
            self.active = False
            self.retracting = True
            return True
        return False
    
    def render(self, surf):
        surf.blit(self.image, self.rect)
        self.close_button.render(surf)


class BasePage():
    def __init__(self, title, game):
        self.g = game
        self.image = generate_glowing_text(game.WIN_SIZE, title, pygame.font.Font(fp, 50), 'white', 'cyan', center=(game.WIN_SIZE[0]/2, 90))
        self.previous = Button((-100, game.WIN_SIZE[1]-75), 'Previous', align='right')
        self.active = False
        self.pushing = False
        self.retracting = False
    
    def process_pushing(self):
        if self.previous.rect.centerx != 80:
            self.previous.rect.x += 20
        else:
            self.pushing = False
    
    def process_retracting(self):
        if self.previous.rect.centerx != -100:
            self.previous.rect.x -= 20
        else:
            self.retracting = False
            self.active = False
    
    def update(self):
        if self.pushing:
            self.process_pushing()
        if self.retracting:
            self.process_retracting()
        if self.previous.update(self.g.dt) and not self.g.menu.retracting_buttons:
            self.retracting = True
        if not self.active:
            return True
        return False
    
    def render(self, surf):
        surf.blit(self.image, (0, 0))
        self.previous.render(surf)


class SpaceshipPage(BasePage):
    def __init__(self, game):
        super().__init__('Spaceship', game)
        self.credits_font = pygame.font.Font(fp, 22)
        self.image = blit_glowing_text(self.image, 'Stellar Credits :', self.credits_font, 'white', 'cyan', topleft=(40, 170))
    
    def set_credits(self, currency):
        self.credits_img = self.credits_font.render(str(currency), True, 'white')
        
    def render(self, surf):
        super().render(surf)
        surf.blit(self.credits_img, (245, 170))


class MissionsPage(BasePage):
    def __init__(self, game):
        super().__init__('Missions', game)


class SuccesPage(BasePage):
    def __init__(self, game):
        super().__init__('SUCCES', game)
        self.best_score_font = pygame.font.Font(fp, 25)
    
    def set_best_score(self, score):
        self.best_score_img = generate_glowing_text(
            self.g.WIN_SIZE, 'best score : '+score, self.best_score_font, 'white', 'cyan', 4, center=(self.g.WIN_SIZE[0]/2, 200), mode=1)
    
    def render(self, surf):
        super().render(surf)
        surf.blit(self.best_score_img, (0, 0))


class SettingsPage(BasePage):
    def __init__(self, game):
        super().__init__('Settings', game)
        self.image = blit_glowing_text(
            self.image, 'sound on/off : press [m]', pygame.font.Font(fp, 18), 'white', 'cyan', 3, center=(game.WIN_SIZE[0]/2, 350))
        self.image = blit_glowing_text(
            self.image, 'press [ECHAP] to quit', pygame.font.Font(fp, 18), 'white', 'cyan', 3, center=(game.WIN_SIZE[0]/2, 400))


class GameOverMenu():
    def __init__(self, game):
        self.g = game
        self.game_over_img = generate_glowing_text(
            game.WIN_SIZE, 'GAME OVER', pygame.font.Font(fp, 63), 'white', 'red', center=(game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 - 150))
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'Time :', pygame.font.Font(fp, 30), 'white', 'cyan', center=(110, game.WIN_SIZE[1]/2 - 60))
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'Stellar Credits :', pygame.font.Font(fp, 30), 'white', 'yellow', center=(game.WIN_SIZE[0]-160, game.WIN_SIZE[1]/2 - 60))
        self.back_to_menu_button = AnimatedButton((game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 + 170), 'Back to Menu')
    
    def set_values(self, best_score=False):
        self.game_over_time_img = pygame.Surface(self.g.WIN_SIZE, pygame.SRCALPHA)
        blit_center(self.game_over_time_img, pygame.font.Font(fp, 40).render(str(self.g.current_time), True, 'cyan'), (110, self.g.WIN_SIZE[1]/2))
        blit_center(self.game_over_time_img, pygame.font.Font(fp, 40).render(str(self.g.current_credits), True, 'orange'), (self.g.WIN_SIZE[0]-160, self.g.WIN_SIZE[1]/2))
        if best_score:
            blit_center(self.game_over_time_img, pygame.font.Font(fp, 30).render('New Best Time !', True, 'yellow'), (self.g.WIN_SIZE[0]/2, self.g.WIN_SIZE[1]/2 + 70))
    
    def update(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if self.back_to_menu_button.update(self.g.dt):
            self.g.reset()
    
    def render(self, surf):
        surf.blit(self.game_over_img, (0, 0))
        surf.blit(self.game_over_time_img, (0, 0))
        self.back_to_menu_button.render(surf)


class Menu():
    def __init__(self, game):
        self.g = game
        self.main = True
        self.image = self.create_main_image(game)
        self.setup_buttons(game)
        self.spaceship_page = SpaceshipPage(game)
        self.mission_page = MissionsPage(game)
        self.succes_page = SuccesPage(game)
        self.settings_page = SettingsPage(game)
        self.credit_page = CreditPage(game)
        self.set_best_score(game.best_score)
        self.set_credits(game.credits)
        self.gom = GameOverMenu(game)
        
    def create_main_image(self, game):
        image = pygame.Surface(game.WIN_SIZE, pygame.SRCALPHA)
        image = blit_glowing_text(image, 'ASTEROID', pygame.font.Font(fp, 63), 'white', 'cyan', center=(game.WIN_SIZE[0]/2, 90))
        image = blit_glowing_text(image, 'SPRINT', pygame.font.Font(fp, 63), 'white', 'cyan', center=(game.WIN_SIZE[0]/2, 160))
        return image
    
    def setup_buttons(self, game):
        self.play_button = AnimatedButton((game.WIN_SIZE[0]/2, game.WIN_SIZE[1]/2 - 50), 'Play', [180, 70], font_size=45)
        
        size = [200, 55]
        self.spaceship_button = Button((85, game.WIN_SIZE[1]/2 + 55), 'Spaceship', size=size, align='right')
        self.mission_button = Button((62, game.WIN_SIZE[1]/2 + 135), 'Missions', size=size, align='right')
        self.succes_button = Button((75, game.WIN_SIZE[1]/2 + 215), 'Succes', size=size, align='right')
        
        self.settings_button = Button((game.WIN_SIZE[0] - 85, game.WIN_SIZE[1]/2 + 55), 'Settings', size=size, align='left')
        self.credits_button = Button((game.WIN_SIZE[0] - 62, game.WIN_SIZE[1]/2 + 135), 'Credits', size=size, align='left')
        self.quit_button = Button((game.WIN_SIZE[0] - 75, game.WIN_SIZE[1]/2 + 215), 'Quit', size=size, align='left')
        
        self.setup_buttons_variables()
    
    def setup_buttons_variables(self):
        self.retracting_buttons = False
        self.pushing_buttons = False
        self.buttons_clickable = True
        
    def set_best_score(self, score):
        self.succes_page.set_best_score(score)
    
    def set_credits(self, currency):
        self.spaceship_page.set_credits(currency)
    
    def retract_buttons(self):
        self.retracting_buttons = True
        self.buttons_clickable = False
        self.credits_button.stop_hovered()
        
    def push_buttons(self):
        self.pushing_buttons = True
    
    def process_button_retracting(self):
        vel = 15
        if self.spaceship_button.rect.right > 0:
            self.play_button.rect.y -= vel*2
            self.spaceship_button.rect.x -= vel
            self.mission_button.rect.x -= vel
            self.succes_button.rect.x -= vel
            self.settings_button.rect.x += vel
            self.credits_button.rect.x += vel
            self.quit_button.rect.x += vel
        else:
            self.retracting_buttons = False
    
    def process_button_pushing(self):
        vel = 15
        if self.play_button.rect.centery != 275:
            self.play_button.rect.y += vel*2
            self.spaceship_button.rect.x += vel
            self.mission_button.rect.x += vel
            self.succes_button.rect.x += vel
            self.settings_button.rect.x -= vel
            self.credits_button.rect.x -= vel
            self.quit_button.rect.x -= vel
        else:
            self.pushing_buttons = False
            self.buttons_clickable = True
    
    def update(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if self.buttons_clickable:
            active_page = False
            if self.play_button.update(self.g.dt):
                self.g.start_game()
            elif self.spaceship_button.update(self.g.dt):
                active_page = True
                self.spaceship_page.active = True
                self.spaceship_page.pushing = True
            elif self.mission_button.update(self.g.dt):
                active_page = True
                self.mission_page.active = True
                self.mission_page.pushing = True
            elif self.succes_button.update(self.g.dt):
                active_page = True
                self.succes_page.active = True
                self.succes_page.pushing = True
            elif self.settings_button.update(self.g.dt):
                active_page = True
                self.settings_page.active = True
                self.settings_page.pushing = True
            elif self.credits_button.update(self.g.dt):
                self.retract_buttons()
                self.credit_page.pushing = True
            elif self.quit_button.update(self.g.dt):
                self.g.quit()
            
            if active_page:
                self.retract_buttons()
                self.main = False
        
        if self.retracting_buttons:
            self.process_button_retracting()
        elif self.pushing_buttons:
            self.process_button_pushing()
        
        if self.spaceship_page.active:
            if self.spaceship_page.update():
                self.push_buttons()
                self.main = True
        elif self.mission_page.active:
            if self.mission_page.update():
                self.push_buttons()
                self.main = True
        elif self.succes_page.active:
            if self.succes_page.update():
                self.push_buttons()
                self.main = True
        elif self.settings_page.active:
            if self.settings_page.update():
                self.push_buttons()
                self.main = True
        elif self.credit_page.activated():
            if self.credit_page.update():
                self.push_buttons()
        
    def render(self, surf):
        if self.main:
            surf.blit(self.image, (0, 0))
        if self.main or self.retracting_buttons:
                self.play_button.render(surf)
                self.spaceship_button.render(surf)
                self.mission_button.render(surf)
                self.succes_button.render(surf)
                self.settings_button.render(surf)
                self.quit_button.render(surf)
                self.credits_button.render(surf)
        if self.spaceship_page.active:
            self.spaceship_page.render(surf)
        elif self.mission_page.active:
            self.mission_page.render(surf)
        elif self.succes_page.active:
            self.succes_page.render(surf)
        elif self.settings_page.active:
            self.settings_page.render(surf)
        elif self.credit_page.activated():
            self.credit_page.render(surf)
