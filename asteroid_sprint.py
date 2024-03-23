
from random import randint, uniform, choice
from time import time, ctime
from sys import exit
import pygame
pygame.init()

from scripts.window import ShaderWindow
from scripts.entities import Player, Asteroid, StellarCredit, load_images
from scripts.vfx import Fire, Line, Polygon
import scripts.menu as menu
import scripts.core as c


class Game():
    def __init__(self):
        self.window = ShaderWindow(c.WIN_SIZE, 'Asteroid Sprint', 'asset\\shaders\\')
        self.display = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.current_time = time()
        self.start_time = time()
        
        self.keys = None
        self.events = []
        
        self.load_data(c.read_file('data\\data.json'))
        self.setup_ui()
        self.menu = menu.Menu(self)
        self.menu_active = True
        self.setup_sound()
        self.asteroid_images = c.load_image_folder('asset\\asteroids\\')
        load_images()
        self.setup_shaders()
        
    def setup_ui(self):
        self.font = 'asset\\orbitron-bold.otf'
        c.fp = self.font
        self.ui_surf = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        self.time_font = pygame.font.Font(self.font, 24)
    
    def setup_sound(self):
        pygame.mixer.music.load('asset\\Screen Saver.mp3')
        pygame.mixer.music.play(-1)
        self.sound = True
        self.sound_switch_timer = 0
    
    def setup_shaders(self):
        self.rage = False
        self.window.load_const_surface('noise_tex', pygame.image.load('asset\\perlin_noise.png').convert())
        self.window.load_const_var('res', c.WIN_SIZE)
        self.window.load_const_var('w', 1.0/c.WIN_SIZE[0])
        self.window.load_const_var('h', 1.0/c.WIN_SIZE[1])
        self.window.load_const_var('max_st', c.MAX_STELLAR_CREDITS)
        self.stars_surf = pygame.Surface(c.WIN_SIZE, pygame.SRCALPHA)
        
    def get_data(self):
        return {
            'time': self.best_score,
            'currency': str(self.credits),
            'magnet': str(self.magnet_power),
            'games_nb': str(self.games_nb)}
    
    def load_data(self, data):
        self.best_score = data['time']
        self.credits = int(data['currency'])
        self.magnet_power = int(data['magnet'])
        self.games_nb = int(data['games_nb'])
        
    def quit(self):
        if not self.game_over and not self.menu_active:
            self.quick_save()
        c.write_file('data\\data.json', self.get_data())
        pygame.quit()
        exit()
    
    def quick_save(self):
        if c.time_to_seconds(self.current_time) > c.time_to_seconds(self.best_score):
            self.best_score = self.current_time
        self.credits += self.current_credits
    
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
        
    def get_events(self):
        c.CLICK = False
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.quit()
        self.events = pygame.event.get()
        for event in self.events:
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
        image = choice(self.asteroid_images)
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
    
    def start_game(self):
        self.menu_active = False
        self.game_start_time = time()
        self.games_nb += 1
        pygame.mouse.set_visible(False)
        # clear asteroids to avoid player crashing when spawning
        if self.player.update(self.dt):
            self.asteroids.clear()
        
    def end_game(self):
        pygame.mouse.set_visible(True)
        # variable switch
        self.player.crash()
        self.fire.alive = False
        self.game_over = True
        self.animation = True
        self.screen_shake = True
        self.timer = 1400
        # rays / particles effect
        for i in range(13):
            self.vfx_particles.append(Line(self.player.rect.center))
        for i in range(60):
            self.vfx_particles.append(Polygon(self.player.rect.center))
        # check for best score
        if c.time_to_seconds(self.current_time) > c.time_to_seconds(self.best_score):
            self.best_score = self.current_time
            self.menu.gom.set_values(best_score=True)
            self.menu.set_best_score(self.current_time)
        else:
            self.menu.gom.set_values()
        # increase credits
        self.credits += self.current_credits
        self.menu.set_credits(self.credits)
    
    def reset(self):
        self.setup_game()
        self.menu_active = True
    
    def setup_game(self):
        self.speed = 6
        self.spawn_rate = 2000
        self.max_spawn_rate = 600
        self.timer = 0
        self.game_over = False
        self.current_credits = 0
        
        self.screen_shake = False
        self.screen_shake_power = 0
        self.animation = False
        
        self.asteroids = []
        self.points = []
        self.particles = []
        self.vfx_particles = []
        
        self.player = Player(*c.MOUSE_POS, self)
        self.fire = Fire(self)
        self.setup_stars()
    
    def run(self):
        self.setup_game()
        circle_radius = 0
        while True:
            self.dt = self.clock.tick(60)
            self.get_events()
            
            # debug
            if self.keys[pygame.K_f]:
                print('fps :', self.clock.get_fps())
                print('speed :', self.speed)
                print('spawn rate :', self.spawn_rate)
                print('max :', self.max_spawn_rate)
                print('-----')
            
            # reset window
            # self.display.fill((10, 0, 60))
            self.display.fill((0, 0, 0, 0))
            
            # update level variables
            if not self.game_over and not self.menu_active:
                self.current_time = ctime(time()-self.game_start_time)[14:19]
                # increase difficulty
                self.speed += 0.06 * self.dt/100
                if self.speed > 30:
                    self.max_spawn_rate = 500
                if self.speed > 50:
                    self.max_spawn_rate = 350
                if self.spawn_rate > self.max_spawn_rate:
                    self.spawn_rate -= 5 * self.dt/100
            
            # dead animation calcul
            if self.animation:
                self.screen_shake_power = round(self.timer/10)+5
                self.timer -= self.dt
                if self.timer <= 0:
                    self.timer = 1 # to avoid division by zero error
                    self.screen_shake = False
                    self.animation = False
                circle_radius = 1/self.timer*100000
            
            # screen shake
            if self.screen_shake:
                offset = randint(0, self.screen_shake_power) - self.screen_shake_power/2
            else:
                offset = 0
            
            # update background stars
            if not self.game_over and not self.menu_active:
                # add new
                if randint(0, 15) == 0:
                    self.add_bkg_star()
                # move it
                for p in self.particles:
                    if not self.game_over and not self.menu_active:
                        p[1] += 0.5
                        if p[1] > c.WIN_SIZE[1]:
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
                    self.timer = self.spawn_rate
            
            # update and render asteroids
            for a in self.asteroids:
                c.blit_center(self.display, pygame.transform.rotate(a.image, a.angle), (a.rect.centerx + offset, a.rect.centery + offset))
                if not self.game_over:
                    a.update(self.speed, self.dt/100)
                    if a.rect.top > c.WIN_SIZE[1]+25:
                        self.asteroids.remove(a)
            
            # update and render points
            if not self.game_over and not self.menu_active:
                if randint(0, 100) == 0 and len(self.points) < c.MAX_STELLAR_CREDITS:
                    self.add_st()
                for p in self.points:
                    if p.update():
                        self.current_credits += p.radius - 2
                    if not p.alive:
                        self.points.remove(p)
            # for p in self.points:
            #     p.render(self.display, offset)
            
            # update and render player
            if not self.menu_active:
                if not self.game_over:
                    if self.player.update(self.dt/100):
                        self.end_game()
                self.fire.update_render(self.display, self.dt)
                c.blit_center(self.display, self.player.image, (self.player.rect.centerx + offset, self.player.rect.centery + offset))
            
            # render dead animation
            if self.animation:
                # circles around the collision
                pygame.draw.circle(self.display, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius, 5)
                pygame.draw.circle(self.display, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius/3, 3)
                # destruction effect
                for p in self.vfx_particles:
                    p.update(self.dt)
                    p.render(self.display)
                    if not p.alive:
                        self.vfx_particles.remove(p)
            
            # shader rage mode
            if self.keys[pygame.K_r]:
                self.rage = True
            elif self.keys[pygame.K_t]:
                self.rage = False
            
            # sound on/off
            if self.sound_switch_timer > 0:
                self.sound_switch_timer -= self.dt
            if self.keys[pygame.K_m] and self.sound_switch_timer <= 0:
                self.switch_sound(by_key=True)
            
            # render and update menu
            self.ui_surf.fill((0, 0, 0, 0))
            if self.menu_active:
                self.menu.update()
                self.menu.render(self.ui_surf)
            if self.game_over:
                self.menu.gom.update()
            
            # indications
            if not self.menu_active and not self.game_over:
                self.ui_surf.blit(self.time_font.render(str(self.current_time), True, 'cyan'), (8, 12))
                st = self.time_font.render(str(self.current_credits)+' ST', True, 'yellow') # Stellar Credits
                self.ui_surf.blit(st, (c.WIN_SIZE[0] - st.get_width() - 8, 12))
            if self.game_over and not self.animation:
                self.menu.gom.render(self.ui_surf)
            
            # self.display.blit(self.ui_surf, (0, 0))
            
            # final render
            self.window.update(self.dt, game_over=self.game_over, sts=self.get_st_points())
            self.window.render(
                tex       = self.display,
                ui_surf   = self.ui_surf,
                fire_tex  = self.fire.get_surf(),
                stars_tex = self.stars_surf,
                )


if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except Exception as crash:
        pygame.quit()
        raise crash
