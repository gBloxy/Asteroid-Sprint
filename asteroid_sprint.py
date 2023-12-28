
from sys import exit
from random import randint, uniform, choice
from time import time, ctime
import pygame
pygame.init()

from scripts.entities import Player, Asteroid
from scripts.vfx import Fire, Line, Polygon, blit_glowing_text
from scripts.utils import load_image_folder, blit_center, read_file, write_file, time_to_seconds
import scripts.menu as menu



class Game():
    def __init__(self):
        self.WIN_SIZE = [525, 650]
        self.window = pygame.display.set_mode(self.WIN_SIZE)
        pygame.display.set_caption('Asteroid Sprint')
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.current_time = time()
        
        self.keys = None
        self.events = []
        self.mouse_pos = (0, 0)
        
        self.best_score = read_file('data\\data.txt')
        self.setup_ui()
        self.menu = menu.Menu(self)
        self.menu_active = True
        self.setup_sound()
        self.asteroid_images = load_image_folder('asset\\asteroids\\')
        
    def setup_ui(self):
        self.font = 'asset/orbitron-bold.otf'
        menu.fp = self.font
        self.game_over_img = pygame.Surface(self.WIN_SIZE, pygame.SRCALPHA)
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'GAME OVER', pygame.font.Font(self.font, 63), 'white', 'red', center=(self.WIN_SIZE[0]/2, self.WIN_SIZE[1]/2 - 150))
        self.game_over_img = blit_glowing_text(
            self.game_over_img, 'Time :', pygame.font.Font(self.font, 46), 'white', 'red', center=(self.WIN_SIZE[0]/2, self.WIN_SIZE[1]/2 - 60))
        self.time_font = pygame.font.Font(self.font, 24)
        self.sound_on_img = pygame.image.load('asset\\sound_on.png').convert_alpha()
        self.sound_off_img = pygame.image.load('asset\\sound_off.png').convert_alpha()
        self.sound_img = self.sound_on_img
        self.back_to_menu_button = menu.AnimatedButton((self.WIN_SIZE[0]/2, self.WIN_SIZE[1]/2 + 170), 'Back to Menu')
        
    def setup_sound(self):
        pygame.mixer.music.load('asset\\Screen Saver.mp3')
        pygame.mixer.music.play()
        self.sound = True
        self.sound_switch_timer = 0
    
    def switch_sound(self):
        self.sound = not self.sound
        if self.sound:
            self.sound_img = self.sound_on_img
            pygame.mixer.music.unpause()
        else:
            self.sound_img = self.sound_off_img
            pygame.mixer.music.pause()
        self.sound_switch_timer = 200
        
    def quit(self):
        write_file('data\\data.txt', self.best_score)
        pygame.quit()
        exit()
        
    def get_events(self):
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.quit()
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.quit()
        self.mouse_pos = pygame.mouse.get_pos()
    
    def add_asteroid(self, pos, size, velocity, image, motion_x):
        self.asteroids.append(Asteroid(pos, size, velocity, image, motion=[motion_x, 1]))
    
    def add_particle(self):
        x = randint(0, self.WIN_SIZE[0])
        radius = randint(1, 3)
        r = randint(180, 220)
        color = (r, r, randint(200, 255))
        p = [x, -10, radius, color]
        self.particles.append(p)
        return p
    
    def spawn_asteroid(self):
        x = randint(0, self.WIN_SIZE[0])
        velocity = uniform(-4, 7)
        radius = randint(40, 90)
        motion_x = uniform(0 if x < 75 else -0.2, 0 if x > self.WIN_SIZE[0]-75 else 0.2)
        image = choice(self.asteroid_images)
        self.add_asteroid((x, -45), radius, velocity, image, motion_x)
        
    def setup_stars(self):
        for i in range(50):
            p = self.add_particle()
            self.particles[self.particles.index(p)][1] = randint(0, self.WIN_SIZE[1])
    
    def start_game(self):
        self.menu_active = False
        self.game_start_time = time()
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
        # ui things to display time under the game over text
        self.game_over_time_img = pygame.Surface(self.WIN_SIZE, pygame.SRCALPHA)
        self.game_over_time_img = blit_glowing_text(self.game_over_img, str(self.current_time),
            pygame.font.Font(self.font, 50), 'white', 'cyan', gaussian_power=6, center=(self.WIN_SIZE[0]/2, self.WIN_SIZE[1]/2))
        # check for best score
        if time_to_seconds(self.current_time) > time_to_seconds(self.best_score):
            self.best_score = self.current_time
            self.game_over_time_img = blit_glowing_text(self.game_over_time_img, 'New Best Score !', pygame.font.Font(self.font, 30), 'white', 'lightgreen', 
                                                        center=(self.WIN_SIZE[0]/2, self.WIN_SIZE[1]/2 + 60), gaussian_power=6)
    
    def reset(self):
        self.setup_game()
        self.menu_active = True
    
    def setup_game(self):
        self.speed = 6
        self.spawn_rate = 2000
        self.max_spawn_rate = 600
        self.timer = 0
        self.game_over = False
        
        self.screen_shake = False
        self.screen_shake_power = 0
        self.animation = False
        
        self.asteroids = []
        self.particles = []
        self.vfx_particles = []
        
        self.player = Player(self.WIN_SIZE[0]//2, self.WIN_SIZE[1]-100, self)
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
            self.window.fill((10,0,60))
            
            # sound on/off
            if self.sound_switch_timer > 0:
                self.sound_switch_timer -= self.dt
            if self.keys[pygame.K_m] and self.sound_switch_timer <= 0:
                self.switch_sound()
            
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
            
            # render background stars
            if not self.game_over and not self.menu_active:
                if randint(0, 15) == 0:
                    self.add_particle()
            for p in self.particles:
                if not self.game_over and not self.menu_active:
                    p[1] += 0.5
                    if p[1] > self.WIN_SIZE[1]:
                       self.particles.remove(p)
                pygame.draw.circle(self.window, p[3], (p[0] + offset/2, p[1] + offset/2), p[2])
            
            # spawn new asteroids
            if not self.game_over:
                self.timer -= self.dt
                if self.timer <= 0:
                    self.spawn_asteroid()
                    self.timer = self.spawn_rate
            
            # update and render asteroids
            for a in self.asteroids:
                blit_center(self.window, pygame.transform.rotate(a.image, a.angle), (a.rect.centerx + offset, a.rect.centery + offset))
                if not self.game_over:
                    a.update(self.speed, self.dt/100)
                    if a.rect.top > self.WIN_SIZE[1]+25:
                        self.asteroids.remove(a)
            
            # update and render player
            if not self.menu_active:
                if not self.game_over:
                    if self.player.update(self.dt/100):
                        self.end_game()
                self.fire.update_render(self.window, self.dt)
                blit_center(self.window, self.player.image, (self.player.rect.centerx + offset, self.player.rect.centery + offset))
            
            # render dead animation
            if self.animation:
                # circles around the collision
                pygame.draw.circle(self.window, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius, 5)
                pygame.draw.circle(self.window, 'white', (self.player.rect.centerx+offset, self.player.rect.centery+offset), circle_radius/3, 3)
                # destruction effect
                for p in self.vfx_particles:
                    p.update(self.dt)
                    p.render(self.window)
                    if not p.alive:
                        self.vfx_particles.remove(p)
            
            # render and update menu
            if self.menu_active:
                self.menu.update()
                self.menu.render(self.window)
            if self.game_over:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if self.back_to_menu_button.update(self.dt):
                    self.reset()
            
            # indications
            if not self.menu_active:
                self.window.blit(self.time_font.render(str(self.current_time), True, 'green'), (8, 12))
            blit_center(self.window, self.sound_img, (25, self.WIN_SIZE[1]-25))
            if self.game_over and not self.animation:
                self.window.blit(self.game_over_img, (0, 0))
                self.window.blit(self.game_over_time_img, (0, 0))
                self.back_to_menu_button.render(self.window)
            
            pygame.display.flip()


try:
    game = Game()
    game.run()
except Exception as crash:
    pygame.quit()
    raise crash
