
from webbrowser import open as open_url
import pygame

import scripts.core as c
from scripts.vfx import blit_glowing_text, generate_glowing_text
from scripts.gui import Button, AnimatedButton, ClickableText, SwitchButton, Slider, SuccessIcon, SuccessLine, Upgrader, Container, TexturedButton


class BasePage():
    def __init__(self, title, game):
        self.g = game
        self.image = generate_glowing_text(c.WIN_SIZE, title, pygame.font.Font(c.fp, 50), 'white', 'cyan', center=(c.WIN_SIZE[0]/2, 90))
        self.ui_elements = []
        self.active = False
        self.pushing = False
        self.retracting = False
        self.previous = Button((-100, c.WIN_SIZE[1]-75), 'Previous', align='right')
        self.previous.set_callback(self.close)
        self.add_widget(self.previous)
    
    def add_widget(self, widget):
        self.ui_elements.append(widget)
    
    def remove_widget(self, widget):
        self.ui_elements.remove(widget)
    
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
    
    def close(self):
        if not self.g.menu.retracting_buttons:
            self.retracting = True
    
    def update(self):
        if self.pushing:
            self.process_pushing()
        elif self.retracting:
            self.process_retracting()
        if not self.active:
            return True
        for widget in self.ui_elements:
            widget.update(self.g.dt)
        return False
    
    def render(self, surf):
        surf.blit(self.image, (0, 0))
        for widget in self.ui_elements:
            widget.render(surf)


class SpaceshipPage(BasePage):
    def __init__(self, game):
        super().__init__('Spaceship', game)
        self.name_font = pygame.font.Font(c.fp, 25)
        self.credits_font = pygame.font.Font(c.fp, 22)
        self.prices_font = pygame.font.Font(c.fp, 18)
        
        sep = 20
        
        self.image = blit_glowing_text(self.image, 'Stellar Credits :', self.credits_font, 'white', 'cyan', topleft=(40, 170))
        self.image = blit_glowing_text(self.image, 'Magnet', self.name_font, 'white', 'cyan', topleft=(80, 250))
        self.image = blit_glowing_text(self.image, 'Time freeze', self.name_font, 'white', 'cyan', topleft=(80, 325 + sep))
        self.image = blit_glowing_text(self.image, 'Repulsion', self.name_font, 'white', 'cyan', topleft=(80, 400 + sep))
        
        text_size = self.name_font.size('Magnet')
        self.upgrader = Upgrader(100 + text_size[0], 248 + text_size[1] / 2)
        self.add_widget(self.upgrader)
        
        self.add_button(self.upgrader, self.upgrade_magnet)
        
        magnet_level = game.magnet_power
        self.upgrader.set(magnet_level)
        if magnet_level < 10:
            self.magnet_price, self.magnet_pos = self.get_price_surf(self.upgrader, self.g.gd.magnet_prices[magnet_level-1])
        
        text_size = self.name_font.size('Time freeze')
        self.freeze = Container(100 + text_size[0], 323 + text_size[1] / 2 + sep)
        self.add_widget(self.freeze)
        
        freeze_nb = game.gd.freezes
        self.freeze.set(freeze_nb)
        if freeze_nb < 3:
            price = self.g.gd.freeze_prices[freeze_nb] if 'freeze' in self.g.gd.powers else self.g.gd.unlock_freeze
            self.freeze_price, self.freeze_pos = self.get_price_surf(self.freeze, price)
        
        self.add_button(self.freeze, self.new_freeze)
        
        text_size = self.name_font.size('Repulsion')
        self.repulsion = Container(126 + text_size[0], 398 + text_size[1] / 2 + sep)
        self.add_widget(self.repulsion)
        
        rep_nb = game.gd.repulsions
        self.repulsion.set(rep_nb)
        if rep_nb < 3:
            price = self.g.gd.repulsion_prices[rep_nb] if 'repulsion' in self.g.gd.powers else self.g.gd.unlock_repulsion
            self.rep_price, self.rep_pos = self.get_price_surf(self.repulsion, price)
        
        self.add_button(self.repulsion, self.new_repulsion)
        
    def add_button(self, parent, callback):
        pos = (parent.rect.right + 30, parent.rect.centery)
        button = TexturedButton(pos, self.g.asset.button, self.g.asset.button_hovered, self.g.asset.button_clicked, callback)
        self.add_widget(button)
    
    def set_credits(self, currency):
        self.credits_img = self.credits_font.render(str(currency), True, 'gold')
    
    def get_price_surf(self, parent, price):
        surf = self.prices_font.render(str(price), True, 'cyan' if self.affordable(price) else 'red')
        pos = (parent.rect.right - surf.get_width() - 10, parent.rect.bottom + 5)
        return surf, pos
    
    def affordable(self, price):
        return price <= self.g.credits
    
    def upgrade_magnet(self):
        level = self.g.magnet_power
        if level < 10:
            price = self.g.gd.magnet_prices[level-1]
            if self.affordable(price):
                self.g.magnet_power += 1
                self.upgrader.increment()
                self.g.purchase(price)
                if level + 1 < 10:
                    self.magnet_price, self.magnet_pos = self.get_price_surf(self.upgrader, self.g.gd.magnet_prices[level])
    
    def new_freeze(self):
        level = self.g.gd.freezes
        if level < 3:
            if 'freeze' in self.g.gd.powers:
                price = self.g.gd.freeze_prices[level]
            else:
                price = self.g.gd.unlock_freeze
            if self.affordable(price):
                if not 'freeze' in self.g.gd.powers:
                    self.g.gd.powers.append('freeze')
                self.g.gd.freezes += 1
                self.g.hud.freeze += 1
                self.freeze.increment()
                self.g.purchase(price)
                if level + 1 < 3:
                    self.freeze_price, self.freeze_pos = self.get_price_surf(self.freeze, self.g.gd.freeze_prices[level+1])
    
    def new_repulsion(self):
        level = self.g.gd.repulsions
        if level < 3:
            if 'repulsion' in self.g.gd.powers:
                price = self.g.gd.repulsion_prices[level]
            else:
                price = self.g.gd.unlock_repulsion
            if self.affordable(price):
                if not 'repulsion' in self.g.gd.powers:
                    self.g.gd.powers.append('repulsion')
                self.g.gd.repulsions += 1
                self.g.hud.repulsion += 1
                self.repulsion.increment()
                self.g.purchase(price)
                if level + 1 < 3:
                    self.rep_price, self.rep_pos = self.get_price_surf(self.repulsion, self.g.gd.repulsion_prices[level + 1])
    
    def lose_freeze(self):
        level = self.g.gd.freezes
        price = self.g.gd.freeze_prices[level]
        self.freeze.decrement()
        self.freeze_price, self.freeze_pos = self.get_price_surf(self.freeze, price)
    
    def lose_repulsion(self):
        level = self.g.gd.repulsions
        price = self.g.gd.repulsion_prices[level]
        self.repulsion.decrement()
        self.rep_price, self.rep_pos = self.get_price_surf(self.repulsion, price)
    
    def render(self, surf):
        super().render(surf)
        surf.blit(self.credits_img, (245, 170))
        if self.g.magnet_power < 10:
            surf.blit(self.magnet_price, self.magnet_pos)
        if self.freeze.level < 3:
            surf.blit(self.freeze_price, self.freeze_pos)
        if self.repulsion.level < 3:
            surf.blit(self.rep_price, self.rep_pos)


class LeaderboardPage(BasePage):
    def __init__(self, game):
        super().__init__('Leaderboard', game)
        self.missions_area = pygame.Rect(0, 140, c.WIN_SIZE[0], 392)
        self.surf = pygame.Surface(self.missions_area.size, pygame.SRCALPHA)
        
    def render(self, surf):
        super().render(surf)


class SuccessPage(BasePage):
    def __init__(self, game):
        super().__init__('Success', game)
        self.high_score_font = pygame.font.Font(c.fp, 25)
        self.selected = None
        
        x, y = 50, 195
        for s in game.gd.success_mgr.success_order:
            self.add_widget(SuccessIcon(x, y, game.gd.get_success(s), self))
            x += 85
            if x > 450:
                x = 50
                y += 85
    
    def select(self, success):
        if self.selected is not None:
            if success == self.selected.success:
                return
            self.ui_elements.remove(self.selected)
        if success is not None:
            self.selected = SuccessLine(185, 538, 325, success)
            self.add_widget(self.selected)
        else:
            self.selected = None
    
    def set_high_score(self, score):
        self.high_score_img = generate_glowing_text(
            c.WIN_SIZE, 'high score : '+str(score), self.high_score_font, 'white', 'cyan', 4, center=(c.WIN_SIZE[0]/2, 156), mode=1)
    
    def close(self):
        super().close()
        self.select(None)
    
    def render(self, surf):
        super().render(surf)
        surf.blit(self.high_score_img, (0, 0))


class SettingsPage(BasePage):
    def __init__(self, game):
        super().__init__('Settings', game)
        self.sound = SwitchButton((120, 200), 'Sound')
        self.sound.set_callback(self.g.switch_sound)
        self.add_widget(self.sound)
        sound_slider = Slider((310, 200), width=200, start_value=1.0, show_val=True)
        sound_slider.set_callback(self.g.set_volume)
        self.add_widget(sound_slider)
        self.setup_indications()
    
    def setup_indications(self):
        self.image = blit_glowing_text(
            self.image, 'sound on/off : press [m]', pygame.font.Font(c.fp, 18), 'white', 'cyan', 3, center=(c.WIN_SIZE[0]/2, 350))
        self.image = blit_glowing_text(
            self.image, 'press [ECHAP] to quit', pygame.font.Font(c.fp, 18), 'white', 'cyan', 3, center=(c.WIN_SIZE[0]/2, 400))
    
    def tg_sound(self):
        self.sound.toggle()


class CreditPage(BasePage):
    def __init__(self, game):
        super().__init__('Credits', game)
        self.setup_text()
        itch_link = ClickableText((296, 386), '@g-bloxy', font_size=14)
        itch_link.set_callback(lambda: open_url(c.ITCH_URL))
        self.add_widget(itch_link)
        github_link = ClickableText((296, 412), '@gBloxy', font_size=14)
        github_link.set_callback(lambda: open_url(c.GITHUB_URL))
        self.add_widget(github_link)
        c.blit_center(self.image, game.asset.logo, (c.WIN_SIZE[0] / 2 + 10, 490))
    
    def add_line(self, text):
        self.line_y += 20
        self.image = blit_glowing_text(self.image, text, self.font, 'white', 'cyan', 3, center=(self.line_x, self.line_y))
    
    def jump_line(self):
        self.line_y += 18
    
    def setup_text(self):
        self.font = pygame.font.Font(c.fp, 14)
        self.line_x, self.line_y = c.WIN_SIZE[0] // 2, 160
        self.add_line('This game was created by g_Bloxy.')
        self.jump_line()
        self.add_line('The spaceship fire trail is a customized version of')
        self.add_line('the fire vfx of @kadir014 on github.')
        self.line_y += 8
        self.add_line('The death particles are a customized version of')
        self.add_line('the vfx of @eliczi on github.')
        self.jump_line()
        self.add_line('Font used : orbitron from the league of moveable type.')
        self.line_y += 4
        self.add_line('Music used : screen saver from Kevin MacLeod.')
        self.jump_line()
        self.line_x -= 37
        self.add_line('itch.io :')
        self.line_y += 6
        self.add_line('github :')


class GameOverMenu():
    def __init__(self, game):
        self.g = game
        self.setup_indications()
        retry_button = AnimatedButton((c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 + 120), 'Retry')
        retry_button.set_callback(self._slot_replay)
        back_to_menu_button = AnimatedButton((c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 + 180), 'Menu')
        back_to_menu_button.set_callback(self.g.reset)
        quit_button = Button((c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 + 240), 'Quit')
        quit_button.set_callback(self.g.quit)
        self.buttons = [retry_button, back_to_menu_button, quit_button]
    
    def setup_indications(self):
        self.game_over_img = generate_glowing_text(
            c.WIN_SIZE, 'GAME OVER', pygame.font.Font(c.fp, 63), 'white', 'red', center=(c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 - 200))
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'Score :', pygame.font.Font(c.fp, 30), 'white', 'cyan', center=(110, c.WIN_SIZE[1]/2 - 110))
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'Stellar Credits :', pygame.font.Font(c.fp, 30), 'white', 'yellow', center=(c.WIN_SIZE[0]-160, c.WIN_SIZE[1]/2 - 110))
    
    def set_values(self, high_score=False):
        self.game_over_time_img = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        c.blit_center(self.game_over_time_img, pygame.font.Font(c.fp, 40).render(str(self.g.score), True, 'cyan'), (110, c.WIN_SIZE[1]/2 - 50))
        c.blit_center(self.game_over_time_img, pygame.font.Font(c.fp, 40).render(str(self.g.current_credits), True, 'orange'), (c.WIN_SIZE[0]-160, c.WIN_SIZE[1]/2 - 50))
        if high_score:
            c.blit_center(self.game_over_time_img, pygame.font.Font(c.fp, 30).render('New High Score !', True, 'yellow'), (c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 + 20))
    
    def _slot_replay(self):
        self.g.reset()
        self.g.start_game()
    
    def update(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for b in self.buttons:
            b.update(self.g.dt)
    
    def render(self, surf):
        surf.blit(self.game_over_img, (0, 0))
        surf.blit(self.game_over_time_img, (0, 0))
        for b in self.buttons:
            b.render(surf)


class Menu():
    def __init__(self, game):
        self.g = game
        self.main = True
        self.image = self.create_main_image(game)
        self.buttons = []
        self.pages = []
        self.setup_pages(game)
        self.setup_buttons(game)
        
    def create_main_image(self, game):
        image = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        font  =  pygame.font.Font(c.fp, 63)
        image = blit_glowing_text(image, 'ASTEROID',font, 'white', 'cyan', center=(c.WIN_SIZE[0]/2, 90))
        image = blit_glowing_text(image, 'SPRINT', font, 'white', 'cyan', center=(c.WIN_SIZE[0]/2, 160))
        return image
    
    def setup_pages(self, game):
        self.spaceship_page = SpaceshipPage(game)
        self.leaderboard_page = LeaderboardPage(game)
        self.succes_page = SuccessPage(game)
        self.settings_page = SettingsPage(game)
        self.credit_page = CreditPage(game)
        self.pages = [self.spaceship_page, self.succes_page, self.leaderboard_page, self.settings_page, self.credit_page]
        self.set_high_score(game.gd.high_score)
        self.set_credits(game.credits)
        self.gom = GameOverMenu(game)
    
    def setup_buttons(self, game):
        self.play_button = AnimatedButton((c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2 - 50), 'Play', [180, 70], font_size=45)
        self.play_button.set_callback(self.g.start_game)
        
        size = [200, 55]
        self.spaceship_button = Button((85, c.WIN_SIZE[1]/2 + 55), 'Spaceship', size=size, align='right')
        self.success_button = Button((62, c.WIN_SIZE[1]/2 + 135), 'Success', size=size, align='right')
        self.leaderboard_button = Button((75, c.WIN_SIZE[1]/2 + 215), 'Rankings', size=size, align='right')
        self.buttons += [self.spaceship_button, self.success_button, self.leaderboard_button]
        
        self.settings_button = Button((c.WIN_SIZE[0] - 85, c.WIN_SIZE[1]/2 + 55), 'Settings', size=size, align='left')
        self.credits_button = Button((c.WIN_SIZE[0] - 62, c.WIN_SIZE[1]/2 + 135), 'Credits', size=size, align='left')
        self.quit_button = Button((c.WIN_SIZE[0] - 75, c.WIN_SIZE[1]/2 + 215), 'Quit', size=size, align='left')
        self.quit_button.set_callback(self.g.quit)
        self.buttons += [self.settings_button, self.credits_button]
        
        self.retracting_buttons = self.pushing_buttons = False
        self.buttons_clickable = True
        
    def set_high_score(self, score):
        self.succes_page.set_high_score(score)
    
    def set_credits(self, currency):
        self.spaceship_page.set_credits(currency)
        
    def retract_buttons(self):
        self.retracting_buttons = True
        self.buttons_clickable = False
        for b in self.buttons:
            b.stop_hovered()
        
    def push_buttons(self):
        self.pushing_buttons = True
    
    def process_button_retracting(self):
        vel = 15
        if self.spaceship_button.rect.right > 0:
            self.play_button.move(0, -vel*2)
            self.spaceship_button.move(-vel, 0)
            self.leaderboard_button.move(-vel, 0)
            self.success_button.move(-vel, 0)
            self.settings_button.move(vel, 0)
            self.credits_button.move(vel, 0)
            self.quit_button.move(vel, 0)
        else:
            self.retracting_buttons = False
    
    def process_button_pushing(self):
        vel = 15
        if self.play_button.rect.centery != 275:
            self.play_button.move(0, vel*2)
            self.spaceship_button.move(vel, 0)
            self.leaderboard_button.move(vel, 0)
            self.success_button.move(vel, 0)
            self.settings_button.move(-vel, 0)
            self.credits_button.move(-vel, 0)
            self.quit_button.move(-vel, 0)
        else:
            self.pushing_buttons = False
            self.buttons_clickable = True
    
    def update(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        if self.buttons_clickable:
            self.play_button.update(self.g.dt)
            self.quit_button.update(self.g.dt)
            
            for i, b in enumerate(self.buttons):
                if b.update(self.g.dt):
                    self.pages[i].active = self.pages[i].pushing = True
                    self.retract_buttons()
                    self.main = False
                    break
        
        if self.retracting_buttons:
            self.process_button_retracting()
        elif self.pushing_buttons:
            self.process_button_pushing()
        
        for page in self.pages:
            if page.active:
                if page.update():
                    self.push_buttons()
                    self.main = True
                break
        
    def render(self, surf):
        if self.main:
            surf.blit(self.image, (0, 0))
        if self.main or self.retracting_buttons:
            self.play_button.render(surf)
            self.quit_button.render(surf)
            for b in self.buttons:
                b.render(surf)
        for page in self.pages:
            if page.active:
                page.render(surf)
