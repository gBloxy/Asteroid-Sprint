
from random import randint, uniform, choice, random
from time import time, ctime
from sys import exit
import pygame
pygame.init()

from scripts.asset import Asset
from scripts.window import ShaderWindow
from scripts.entities import Asteroid, StellarCredit, Bonus
from scripts.player import Player
from scripts.vfx import Fire, Line, Polygon
from scripts.gamedata import GameDataManager
from scripts.menu import Menu
# from scripts.client import Client # for the leaderboard
import scripts.gui as gui
import scripts.core as c


class Game():
    def __init__(self):
        self.window = ShaderWindow(c.WIN_SIZE, 'Asteroid Sprint', 'shaders/')
        self.window.loading_screen('asset/ui/loading.png')
        self.display = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.current_time = time()
        self.start_time = time()
        
        self.keys = None
        
        self.gd = GameDataManager(self)
        self.load_data()
        self.asset = Asset()
        self.asset.load_assets()
        self.setup_sound()
        self.setup_ui()
        gui.game = self
        self.menu = Menu(self)
        self.menu_active = True
        self.setup_shaders()
        self.hud = gui.EffectsHud()
        
    def setup_ui(self):
        self.font = 'asset/orbitron-bold.otf'
        c.fp = self.font
        self.ui_surf = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        self.time_font = pygame.font.Font(self.font, 26)
    
    def setup_sound(self):
        pygame.mixer.music.load('asset/Screen Saver.mp3')
        pygame.mixer.music.play(-1)
        self.sound = True
        self.sound_switch_timer = 0
    
    def setup_shaders(self):
        self.window.load_const_surface('noise_tex', self.asset.noise)
        self.window.load_const_var('res', c.WIN_SIZE)
        self.window.load_const_var('w', 1.0/c.WIN_SIZE[0])
        self.window.load_const_var('h', 1.0/c.WIN_SIZE[1])
        self.window.load_const_var('max_st', c.MAX_STELLAR_CREDITS)
        self.window.load_const_var('max_magnet', c.MAGNET_DURATION)
        self.window.load_const_var('max_freeze', c.FREEZE_DURATION)
        self.stars_surf = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        
    def load_data(self):
        self.credits = self.gd.credits
        self.magnet_power = self.gd.magnet_power
        
    def quit(self):
        if not self.game_over and not self.menu_active:
            self.gd.check_high_score(self.score)
        self.gd.save_data()
        pygame.quit()
        exit()
    
    def switch_sound(self, by_key=False):
        self.sound = not self.sound
        if self.sound:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        if by_key:
            self.menu.settings_page.tg_sound()
        self.sound_switch_timer = 200
    
    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
    
    def purchase(self, price):
        self.credits -= price
        self.menu.set_credits(self.credits)
    
    def get_events(self):
        c.CLICK = False
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.quit()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    c.CLICK = True
            elif event.type == pygame.QUIT:
                self.quit()
        c.MOUSE_POS = pygame.mouse.get_pos()
    
    def spawn_asteroid(self):
        x = randint(0, c.WIN_SIZE[0])
        velocity = uniform(-4, 7)
        radius = randint(40, 90)
        motion_x = uniform(0 if x < 75 else -0.2, 0 if x > c.WIN_SIZE[0]-75 else 0.2)
        image = choice(self.asset.asteroids)
        self.asteroids.append(Asteroid((x, -50), radius, velocity, image, motion=[motion_x, 1]))
    
    def add_bkg_star(self):
        x = randint(0, c.WIN_SIZE[0])
        radius = choice([1, 1, 1, 2, 2, 3])
        r = randint(180, 220)
        color = (r, r, randint(200, 255))
        p = [x, -10, radius, color]
        self.particles.append(p)
        return p
    
    def setup_stars(self):
        for i in range(50):
            p = self.add_bkg_star()
            self.particles[self.particles.index(p)][1] = randint(0, c.WIN_SIZE[1])
    
    def add_st(self):
        x = randint(0, c.WIN_SIZE[0])
        radius = choice([3, 3, 4])
        vel = randint(-2, 3)
        self.points.append(StellarCredit(x, -10, radius, vel, self))
    
    def get_st_points(self):
        sts = [(st.x, st.y, st.radius) for st in self.points]
        if len(sts) < c.MAX_STELLAR_CREDITS:
            sts += [(-1., -1., -1.) for i in range(c.MAX_STELLAR_CREDITS - len(sts))]
        return sts
    
    def add_bonus(self):
        x = randint(0, c.WIN_SIZE[0])
        velocity = randint(0, 5)
        if random() > 0.6:
            img = self.asset.shield
            callback = lambda: self.player.set_shield(5000)
        elif self.super_magnet > 0 or self.freeze > 0:
            return
        else:
            img = self.asset.magnet
            callback = lambda: self.set_super_magnet(c.MAGNET_DURATION)
        self.bonuses.append(Bonus(x, -10, velocity, callback, img, self))
    
    def set_super_magnet(self, duration):
        self.super_magnet = duration
        self.freeze = 0
    
    def set_freeze(self, duration):
        self.freeze = duration
        self.super_magnet = 0
    
    def set_popup(self, message):
        self.popup = gui.PopUp(message)
    
    def start_game(self):
        self.menu_active = False
        self.game_start_time = time()
        self.gd.incr_game_nb()
        pygame.mouse.set_visible(False)
        self.asteroids.clear()
        self.spawn_asteroid()
        self.first_asteroid = self.asteroids[0]
        self.player.rect.center = c.MOUSE_POS
        
    def end_game(self):
        pygame.mouse.set_visible(True)
        
        # variable switch
        collided = self.player.crash()
        self.hud.stop()
        self.fire.alive = False
        self.game_over = True
        self.animation = True
        self.screen_shake = True
        self.timer = 1400
        self.super_magnet = 0
        self.freeze = 0
        
        # rays / particles effect
        for i in range(13):
            self.vfx_particles.append(Line(self.player.rect.center))
        for i in range(60):
            self.vfx_particles.append(Polygon(self.player.rect.center))
        
        # check for best score
        if self.gd.check_high_score(self.score):
            self.menu.gom.set_values(high_score=True)
            self.menu.set_high_score(self.score)
        else:
            self.menu.gom.set_values()
        
        # increase credits
        self.credits += self.current_credits
        self.menu.set_credits(self.credits)
        
        # check for success
        if not self.gd.get_success('moron').unlocked:
            if collided == self.first_asteroid:
                self.gd.success_mgr.unlock('moron')
        self.first_asteroid = None
    
    def reset(self):
        self.setup_game()
        self.menu_active = True
    
    def setup_game(self):
        self.game_over = False
        self.speed = 6
        self.spawn_rate = 2000
        self.max_spawn_rate = 600
        self.timer = 0
        
        self.score = 0
        self.next_time = time() + c.SCORE_DELAY
        self.current_credits = 0
        
        self.super_magnet = 0
        self.freeze = 0
        self.power_timer = 0
        
        self.screen_shake = False
        self.screen_shake_power = 0
        self.animation = False
        
        self.asteroids = []
        self.points = []
        self.bonuses = []
        self.particles = []
        self.vfx_particles = []
        
        self.player = Player(self)
        self.fire = Fire(self)
        self.setup_stars()
        self.popup = None
    
    def run(self):
        self.setup_game()
        circle_radius = 0
        while True:
            self.dt = self.clock.tick(60)
            self.get_events()
            
            # debug
            if c.DEBUG:
                if self.keys[pygame.K_f]:
                    print('fps :', self.clock.get_fps())
                    print('speed :', self.speed)
                    print('spawn rate :', self.spawn_rate)
                    print('max :', self.max_spawn_rate)
                    print('-----')
                if self.keys[pygame.K_KP1]:
                    self.player.set_shield(c.SHIELD_DURATION)
                if self.keys[pygame.K_KP2]:
                    self.set_super_magnet(c.MAGNET_DURATION)

            # reset window
            # self.display.fill((10, 0, 60))
            self.display.fill((0, 0, 0, 0))
            
            speed = self.speed
            spawn_rate = self.spawn_rate
            rot_speed = 1
            
            # update level variables
            if not self.game_over and not self.menu_active:
                t = time()
                self.current_time = ctime(t - self.game_start_time)[14:19]
                
                # increase score
                if t >= self.next_time:
                    self.score += 20
                    self.next_time = t + c.SCORE_DELAY
                
                # check for time success
                if not 'time.0' in self.gd.success_mgr.unlocked:
                    if int(self.current_time[3:]) == 30:
                        self.gd.success_mgr.unlock('time.0')
                elif int(self.current_time[3:]) == 0: # every minute
                    self.gd.check_time_success(int(self.current_time[:2]))
                
                # increase difficulty
                self.speed += 0.0006 * self.dt
                if self.speed > 30:
                    self.max_spawn_rate = 500
                if self.speed > 50:
                    self.max_spawn_rate = 350
                if self.spawn_rate > self.max_spawn_rate:
                    self.spawn_rate -= 0.05 * self.dt
                
                # powers timer update
                if self.power_timer > 0:
                    self.power_timer -= self.dt
                
                # super magnet effect update
                if self.super_magnet > 0:
                    self.super_magnet -= self.dt
                    speed = self.speed + 30
                    spawn_rate = self.spawn_rate - 75
                    rot_speed = 2
                
                # freeze effect update
                if self.freeze > 0:
                    self.freeze -= self.dt
                    speed = 2
                    spawn_rate = 2000
                    rot_speed = 0.2
            
            # dead animation calcul
            if self.animation:
                self.screen_shake_power = round(self.timer/10)+5
                self.timer -= self.dt
                if self.timer <= 0:
                    self.timer = 1 # to avoid division by zero error
                    self.screen_shake = False
                    self.animation = False
                circle_radius = 100000/self.timer
            
            # screen shake
            if self.screen_shake:
                offset = randint(0, self.screen_shake_power) - self.screen_shake_power/2
            else:
                offset = 0
            
            # update background stars
            if not self.game_over and not self.menu_active:
                # add new
                if self.super_magnet <= 0:
                    if random() < c.STARS_PROB:
                        self.add_bkg_star()
                    vel = 0.5
                else:
                    if random() < 0.35:
                        self.add_bkg_star()
                    vel = 7
                # move it
                for p in self.particles:
                    if not self.game_over and not self.menu_active:
                        p[1] += vel
                        if p[1] > c.WIN_SIZE[1] + 20:
                           self.particles.remove(p)
            
            # render stars
            self.stars_surf.fill((0, 0, 0, 0))
            for p in self.particles:
                pygame.draw.circle(self.stars_surf, p[3], (p[0] + offset/2, p[1] + offset/2), p[2])
            self.display.blit(self.stars_surf, (0, 0))
            
            # spawn new asteroids
            if not self.game_over:
                self.timer -= self.dt
                if self.timer <= 0:
                    self.spawn_asteroid()
                    self.timer = spawn_rate
            
            # update and render asteroids
            for a in self.asteroids:
                c.blit_center(self.display, pygame.transform.rotate(a.image, a.angle), (a.rect.centerx + offset, a.rect.centery + offset))
                if not self.game_over:
                    a.update(speed, rot_speed, self.dt/100)
                    if a.rect.top > c.WIN_SIZE[1]+25 or a.rect.left > c.WIN_SIZE[0]+25 or a.rect.right < -25:
                        self.asteroids.remove(a)
            
            # update and render stellar credits
            magnet_power = self.magnet_power if self.super_magnet <= 0 else 20
            
            if not self.game_over and not self.menu_active:
                if random() < (0.01 if self.super_magnet <= 0 else 0.05) and len(self.points) < c.MAX_STELLAR_CREDITS:
                    self.add_st()
                for p in self.points:
                    p.update(speed, magnet_power, self.dt/100)
                    if not p.alive:
                        self.points.remove(p)
            # for p in self.points:
            #     p.render(self.display, offset)
            
            # update and render bonuses
            if not self.game_over and not self.menu_active:
                if random() < c.BONUSES_PROB:
                    self.add_bonus()
                for b in self.bonuses:
                    b.update(speed, magnet_power, self.dt/100)
                    if not b.alive:
                        self.bonuses.remove(b)
                    else:
                        b.render(self.display, offset)
            
            # actions
            if not self.menu_active:
                if not self.game_over:
                    if self.keys[pygame.K_SPACE]:
                        self.hud.show()
                    if self.power_timer <= 0:
                        if self.keys[pygame.K_a] and self.gd.freezes > 0:
                            self.set_freeze(c.FREEZE_DURATION)
                            self.gd.freezes -= 1
                            self.menu.spaceship_page.lose_freeze()
                            self.hud.lose_freeze()
                            self.power_timer = c.POWER_DELAY
                        if self.keys[pygame.K_e] and self.gd.repulsions > 0:
                            self.player.repulse()
                            self.gd.repulsions -= 1
                            self.menu.spaceship_page.lose_repulsion()
                            self.hud.lose_repulsion()
                            self.power_timer = c.POWER_DELAY
            
            # update and render player
                    if self.player.update(self.dt/100):
                        self.end_game()
                    
                    self.hud.update(self.dt, self.display)
                    
                self.fire.update_render(self.display, self.dt)
                self.player.render(self.display, offset)
            
            # render dead animation / circles around the collision
            if self.animation:
                pygame.draw.circle(self.display, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius, 5)
                pygame.draw.circle(self.display, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius/3, 3)
            
            # update and render vfx particles (dead anim and shield breaking)
            for p in self.vfx_particles:
                p.update(self.dt)
                p.render(self.display)
                if not p.alive:
                    self.vfx_particles.remove(p)
            
            # sound on/off
            if self.sound_switch_timer > 0:
                self.sound_switch_timer -= self.dt
            if self.keys[pygame.K_m] and self.sound_switch_timer <= 0:
                self.switch_sound(by_key=True)
            
            # update and render menu
            self.ui_surf.fill((0, 0, 0, 0))
            if self.menu_active:
                self.menu.update()
                self.menu.render(self.ui_surf)
            if self.game_over:
                self.menu.gom.update()
            
            # indications
            if not self.menu_active and not self.game_over:
                score = self.time_font.render(str(self.score), True, 'cyan')
                self.ui_surf.blit(score, (c.WIN_SIZE[0] / 2 - score.get_width() / 2, 14))
                st = self.time_font.render(str(self.current_credits)+' ST', True, 'yellow') # Stellar Credits
                self.ui_surf.blit(st, (c.WIN_SIZE[0] - st.get_width() - 8, 14))
            if self.game_over and not self.animation:
                self.menu.gom.render(self.ui_surf)
            
            # update and render success and mission screen popup
            if self.popup:
                if self.popup.update(self.dt):
                    self.popup = None
                else:
                    self.popup.render(self.ui_surf)
            
            # self.display.blit(self.ui_surf, (0, 0))
            
            # final render
            self.window.update(
                self.dt,
                game_over  = self.game_over,
                sts        = self.get_st_points(),
                player_pos = self.player.rect.center,
                repulse_ti = self.player.repulse_delay,
                shield     = self.player.shield,
                magnet     = self.super_magnet,
                freeze     = self.freeze,
                menu       = self.menu_active,
                mouse      = c.MOUSE_POS
                )
            self.window.render(
                tex       = self.display,
                ui_surf   = self.ui_surf,
                fire_tex  = self.fire.get_surf(),
                stars_tex = self.stars_surf
                )
            
            pygame.display.set_caption('Asteroid Sprint - FPS: '+str(int(self.clock.get_fps())))


if __name__ == '__main__':
    game = Game()
    game.run()
