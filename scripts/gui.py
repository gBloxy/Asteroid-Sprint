
import pygame

from scripts.vfx import blit_glowing_text, generate_glowing_text
import scripts.core as c


game = None # futur reference to the main game class instance


class Button():
    def __init__(self, center, text, font_size=26, size=None, border=True, gaussian_power=5, align='center'):
        self.image = pygame.Surface((400, 100), pygame.SRCALPHA)
        self.image = blit_glowing_text(
            self.image, text, pygame.font.Font(c.fp, font_size), 'white', 'cyan', gaussian_power, center=(self.image.get_width()/2, self.image.get_height()/2))
        self.image_rect = self.image.get_rect(center=center)
        self.text_size = list(pygame.font.Font(c.fp, font_size).render(text, True, 'white').get_size())
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
        self.callback = None
    
    def set_callback(self, func):
        self.callback = func
    
    def move(self, x, y):
        self.rect.move_ip(x, y)
    
    def click(self):
        if self.callback is not None:
            self.callback()
        
    def update_state(self):
        self.clicked = False
        if self.rect.collidepoint(c.MOUSE_POS):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.hovered = True
            if c.CLICK:
                self.clicked = True
        else:
            self.hovered = False
    
    def stop_hovered(self):
        self.hovered = False
        self.border_width = 3
        center = self.rect.center
        self.rect = self.normal_rect.copy()
        self.rect.center = center
    
    def update(self, dt=None):
        self.update_state()
        if self.hovered:
            if self.rect.width < self.max_size:
                c.increase_rect(self.rect, (2, 0))
                self.border_width += 0.08
            if self.clicked:
                self.click()
                return True
        else:
            if self.rect.width > self.min_size:
                c.increase_rect(self.rect, (-2, 0))
                self.border_width -= 0.08
        return False
    
    def render(self, surf):
        if self.align == 'center':
            c.blit_center(surf, self.image, self.rect.center)
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
                c.increase_rect(self.rect, (2, 0))
                self.border_width += 0.08
            if self.clicked and not self.animated:
                self.animated = True
        else:
            if self.rect.width > self.min_size:
                c.increase_rect(self.rect, (-2, 0))
                self.border_width -= 0.08
        if self.animated:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                self.animation_timer = 450
                self.animated = False
                self.rect = self.normal_rect.copy()
                self.border_width = 3
                self.click()
                return True
            center = self.rect.center
            self.rect.width += 30
            self.rect.height += 30
            self.rect.center = center
        return False


class TexturedButton():
    def __init__(self, center, image, image_hovered=None, image_clicked=None, callback=None):
        self.image = image
        self.image_hovered = image_hovered if image_hovered else image
        self.image_clicked = image_clicked if image_clicked else image
        self.rect = image.get_rect(center=center)
        self.callback = callback
        self.hovered = False
        self.timer = 0
    
    def click(self):
        self.timer = 200
        if self.callback:
            self.callback()
    
    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
        if self.rect.collidepoint(c.MOUSE_POS):
            self.hovered = True
            if c.CLICK:
                self.click()
        else:
            self.hovered = False
    
    def render(self, surf):
        if self.timer > 0:
            surf.blit(self.image_clicked, self.rect)
        elif self.hovered:
            surf.blit(self.image_hovered, self.rect)
        else:
            surf.blit(self.image, self.rect)


# class SimpleButton():
#     def __init__(self, center, text, callback=None, color='black'):
#         self.image = pygame.font.Font(c.fp, 16).render(text, True, color)
#         self.rect = self.image.get_rect(center=center)
#         c.increase_rect(self.rect, (14, 10))
        
#         self.callback = callback
#         self.color = color
        
#         self.min_size = self.rect.width
#         self.max_size = self.rect.width + 8
#         self.border_width = 2
        
#     def move(self, x, y):
#         self.rect.move_ip(x, y)
    
#     def click(self):
#         if self.callback is not None:
#             self.callback()
    
#     def update(self, dt=None):
#         if self.rect.collidepoint(c.MOUSE_POS):
#             if self.rect.width < self.max_size:
#                 c.increase_rect(self.rect, (2, 1))
#                 self.border_width += 0.08
#             if c.CLICK:
#                 self.click()
#                 return True
#         else:
#             if self.rect.width > self.min_size:
#                 c.increase_rect(self.rect, (-2, -1))
#                 self.border_width -= 0.08
#         return False
    
#     def render(self, surf, y=0):
#         c.blit_center(surf, self.image, (self.rect.centerx + 1, self.rect.centery - y + 2))
#         pygame.draw.rect(surf, self.color, pygame.Rect(self.rect.x, self.rect.y - y, *self.rect.size), width=round(self.border_width), border_radius=15)


class ClickableText(Button):
    def __init__(self, center, text, mode='underlined', font_size=18):
        super().__init__(center, text, font_size=font_size, border=False, gaussian_power=5)
        self.rect = pygame.Rect(0, 0, *self.text_size)
        self.rect.center = center
        self.mode = mode
    
    def update(self, dt=None):
        self.update_state()
        if self.hovered and self.clicked:
            self.click()
            return True
        return False
    
    def render(self, surf):
        if self.hovered:
            if self.mode == 'underlined':
                super().render(surf)
                pygame.draw.rect(surf, 'lightblue', (self.rect.left, self.rect.bottom-3, self.rect.width, 2))
            elif self.mode == 'zoomed':
                c.blit_center(surf, pygame.transform.scale(self.image, (self.image.get_width()+15, self.image.get_height()+15)), self.image_rect.center)
        else:
            super().render(surf)


class SwitchButton():
    def __init__(self, center, text, activated=True):
        font = pygame.font.Font(c.fp, 18)
        rendered_text = font.render(text, True, 'black')
        size = rendered_text.get_size()
        self.text_img = generate_glowing_text((size[0]+6, size[1]+6), text, font, 'white', 'cyan', center=(size[0]/2+3, size[1]/2+3), gaussian_power=3, mode=1)
        self.img_rect = self.text_img.get_rect()
        self.rect = pygame.Rect(0, 0, 50, 25)
        self.state = activated
        self.callback = None
        self.move(center)
    
    def move(self, center):
        self.img_rect.midright = (center[0] - 5, center[1] + 2)
        self.rect.midleft = (center[0] + 5, center[1])
    
    def set_callback(self, func):
        self.callback = func
    
    def _toggle(self):
        self.state = not self.state
        if self.callback is not None:
            self.callback()
    
    def toggle(self):
        self.state = not self.state
    
    def update(self, dt=None):
        if self.rect.collidepoint(c.MOUSE_POS):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if c.CLICK:
                self._toggle()
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
    def __init__(self, center, width=150, start_value=0.5, show_val=False):
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
        
        self.font = pygame.font.Font(c.fp, 16)
        
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
    
    def update(self, dt=None):
        if pygame.mouse.get_pressed()[0] and self.bar_rect.collidepoint(c.MOUSE_POS):
            old = self.value
            new = (c.MOUSE_POS[0] - self.bar_rect.x) / self.width
            if old != new:
                self.set_value(new)
                if self.callback is not None:
                    self.callback(self.value)
    
    def render(self, surf):
        c.blit_center(surf, self.bar_img, self.center)
        pygame.draw.rect(surf, 'lightblue', self.cursor_rect, border_radius=5)
        if self.text_img is not None:
            c.blit_center(surf, self.text_img, self.text_co)


class CellsBar():
    def __init__(self, img, left, centery, max):
        self.img = img
        self.rect = self.img.get_rect(left=left, centery=centery)
        self.level = 0
        self.cell_y = self.rect.top + 4
        self.max = max
    
    def set(self, level):
        self.level = level
    
    def increment(self):
        self.level = min(self.level + 1, self.max)
    
    def update(self, dt=None):
        pass
    
    def render(self, surf):
        surf.blit(self.img, self.rect)


class Upgrader(CellsBar):
    def __init__(self, left, centery):
        super().__init__(game.asset.upgrade_bar, left, centery, 10)
        self.colors = ['yellow', 'gold', 'orange', 'darkorange', 'tomato', 'orangered', 'red', 'crimson', 'firebrick', 'darkred']
        self.cells = []
        for i in range(self.max):
            self.cells.append(c.swap_color(game.asset.upgrade_cell.copy(), 'white', self.colors[i]))
    
    def render(self, surf):
        super().render(surf)
        x = self.rect.right - 40
        for i in range(self.level):
            surf.blit(self.cells[i], (x, self.cell_y))
            x -= 16


class Container(CellsBar):
    def __init__(self, left, centery):
        super().__init__(game.asset.container_bar, left, centery, 3)
        self.cell = c.swap_color(game.asset.container_cell.copy(), 'white', 'cyan')
    
    def decrement(self):
        self.level = max(self.level - 1, 0)
    
    def render(self, surf):
        super().render(surf)
        x = self.rect.right - 56
        for i in range(self.level):
            surf.blit(self.cell, (x, self.cell_y))
            x -= 32


class SuccessLine():
    def __init__(self, x, y, width, success):
        self.success = success
        self.rect = pygame.Rect(x, y, width, 70)
        self.icon_pos = (self.rect.x + 8, self.rect.y + 7)
        
        font = pygame.font.Font(c.fp, 13)
        text = font.render(success.description, True, 'lightgray')
        
        if text.get_width() > width - 75:
            line_wrapped = True
            self.rect.h += 17
        else:
            line_wrapped = False
        
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.surface, (50., 50., 50., 120), (0, 0, *self.rect.size), border_radius=10)
        pygame.draw.rect(self.surface, 'lightblue', (0, 0, *self.rect.size), width=3, border_radius=10)
        
        self.surface.blit(pygame.font.Font(c.fp, 17).render(success.title, True, 'white'), (70, 15))
        if line_wrapped:
            c.line_wrapp(self.surface, success.description, 'lightgray', pygame.Rect(70, 40, width - 75, 50), font)
        else:
            self.surface.blit(text, (70, 40))
        
    def update(self, dt=None):
        pass
    
    def render(self, surf):
        surf.blit(self.surface, self.rect)
        surf.blit(self.success.icon, self.icon_pos)


class SuccessIcon():
    def __init__(self, x, y, success, parent):
        self.parent = parent
        self.success = success
        self.rect = pygame.Rect(x, y, 70, 70)
        self.bkg = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.bkg, (50, 50, 50, 120), (0, 0, *self.rect.size), border_radius=10)
    
    def update(self, dt=None):
        if self.rect.collidepoint(c.MOUSE_POS):
            if self.rect.height < 77:
                c.increase_rect(self.rect, (1, 1))
            if c.CLICK:
                if self.success.unlocked or not self.success.hidden:
                    self.parent.select(self.success)
        elif self.rect.height > 70:
            c.increase_rect(self.rect, (-1, -1))
    
    def render(self, surf):
        pygame.draw.rect(surf, (50, 50, 50, 120), self.rect, border_radius=10)
        pygame.draw.rect(surf, 'lightblue', self.rect, width=3, border_radius=10)
        c.blit_center(surf, self.success.icon, self.rect.center)


class PopUp():
    speed = 20
    time  = 2000
    width = 280
    def __init__(self, text):
        self.rect = pygame.Rect(c.WIN_SIZE[0], 70, self.width, 66)
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        pygame.draw.rect(self.surface, (50., 50., 50., 120), (0, 0, *self.rect.size), border_radius=20)
        pygame.draw.rect(self.surface, 'lightblue', (0, 0, *self.rect.size), width=3, border_radius=20)
        
        self.surface.blit(game.asset.icon_success, (5, 5))
        self.surface.blit(pygame.font.Font(c.fp, 15).render('Achievement Unlocked', True, 'white'), (65, 15))
        self.surface.blit(pygame.font.Font(c.fp, 15).render(text, True, 'lightgray'), (65, 37))
        
        self.timer = 0
        self.opening = True
        self.waiting = self.closing = False
    
    def update(self, dt):
        if self.opening:
            if self.rect.left > c.WIN_SIZE[0] - self.width + 16:
                self.rect.left = max(c.WIN_SIZE[0] - self.width + 16, self.rect.left - self.speed)
            else:
                self.opening = False
                self.waiting = True
                self.timer = self.time
        elif self.waiting:
            self.timer -= dt
            if self.timer <= 0:
                self.waiting = False
                self.closing = True
        elif self.closing:
            if self.rect.left < c.WIN_SIZE[0]:
                self.rect.left += self.speed
            else:
                return True
    
    def render(self, surf):
        surf.blit(self.surface, self.rect)


class EffectsHud():
    def __init__(self):
        self.start_angle_f = 2.487
        self.start_angle_r = 0.654
        self.step_angle = 0.393
        self.gap = self.step_angle + 0.1
        
        self.freeze = game.gd.freezes
        self.repulsion = game.gd.repulsions
        
        self.show_ti = 0
        self.losing_f = 0
        self.losing_r = 0
        
        self._rect = None
    
    @property
    def rect(self):
        if self._rect:
            return self._rect
        else:
            self._rect = (game.player.rect.left - 37, game.player.rect.y - 37, 124, 124)
            return self._rect
    
    def show(self):
        self.show_ti = 3000
    
    def lose_freeze(self):
        self.losing_f = 1500
    
    def lose_repulsion(self):
        self.losing_r = 1500
    
    def stop(self):
        self.show_ti = self.effect_ti = 0
        if self.losing_f > 0:
            self.losing_f = 0
            self.freeze -= 1
        if self.losing_r > 0:
            self.losing_r = 0
            self.repulsion -= 1
    
    def update(self, dt, surf):
        visible = self.show_ti > 0
        self._rect = None
        
        if game.power_timer > 0:
            self.render_timer(surf)
        
        if self.losing_f > 0:
            self.losing_f -= dt
            self.render_freeze(surf, losing=True)
            if self.losing_f <= 0:
                self.losing_f = 0
                self.freeze -= 1
        
        elif visible:
            self.render_freeze(surf)
        
        if self.losing_r > 0:
            self.losing_r -= dt
            self.render_repulsion(surf, losing=True)
            if self.losing_r <= 0:
                self.losing_r = 0
                self.repulsion -= 1
        
        elif visible:
            self.render_repulsion(surf)
        
        if visible:
            self.show_ti -= dt
    
    def render_freeze(self, surf, losing=False):
        if losing:
            color = 'white' if (self.losing_f // 400) % 2 == 0 else 'darkred'
            pygame.draw.arc(surf, color, self.rect, self.start_angle_f, self.start_angle_f + self.step_angle, 5)
        for i in range(0 if not losing else 1, self.freeze):
            d = self.gap * i
            pygame.draw.arc(surf, 'lightblue', self.rect, self.start_angle_f + d, self.start_angle_f + self.step_angle + d, 5)
    
    def render_repulsion(self, surf, losing=False):
        if losing:
            color = 'white' if (self.losing_r // 400) % 2 == 0 else 'darkred'
            pygame.draw.arc(surf, color, self.rect, self.start_angle_r - self.step_angle, self.start_angle_r, 5)
        for i in range(0 if not losing else 1, self.repulsion):
            d = self.gap * i
            pygame.draw.arc(surf, 'orangered', self.rect, self.start_angle_r - self.step_angle - d, self.start_angle_r - d, 5)
    
    def render_timer(self, surf):
        rect = (game.player.rect.left - 30, game.player.rect.top - 30, 110, 110)
        end = c.PI_2 - max(1 - game.power_timer / c.POWER_DELAY, 0) * c.TWO_PI
        pygame.draw.arc(surf, 'gold', rect, c.PI_2, end, 2)
