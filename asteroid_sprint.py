
from sys import exit
from random import randint, uniform, choice
from time import time, ctime
import pygame
pygame.init()

from entities import Player, Asteroid, load_images
from vfx import Fire, Line, Polygon


def blit_center(surface, surf, center):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2))


class Game():
    def __init__(self):
        self.WIN_SIZE = [525, 650]
        self.window = pygame.display.set_mode(self.WIN_SIZE)
        pygame.display.set_caption('Asteroid Sprint')
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.game_start_time = time()
        self.current_time = time()
        
        self.keys = None
        self.events = []
        self.mouse_pos = (0, 0)
        
        self.setup_ui()
        
        self.asteroid_images = load_images('asset\\asteroids\\')
    
    def setup_ui(self):
        self.game_over_msg = pygame.font.SysFont('impact', 80).render('GAME OVER', True, 'red')
        self.game_over_msg_pos = (self.WIN_SIZE[0]/2 - self.game_over_msg.get_width()/2,
                                  self.WIN_SIZE[1]/2 - self.game_over_msg.get_height()/2 - 80)
        self.time_font = pygame.font.SysFont('impact', 25)
        self.time_msg_font = pygame.font.SysFont('impact', 50)
        self.time_msg = pygame.font.SysFont('impact', 45).render('Time :', True, 'red')
        self.time_msg_pos = (self.WIN_SIZE[0]/2 - self.time_msg.get_width()/2, self.game_over_msg_pos[1]+110)
        
    def get_events(self):
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
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
    
    def end_game(self):
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
        self.time_passed = self.time_msg_font.render(str(self.current_time), True, 'green')
        self.time_passed_pos = (self.WIN_SIZE[0]/2 - self.time_passed.get_width()/2, self.time_msg_pos[1] + 55)
    
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
            if not self.game_over:
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
            if not self.game_over:
                if randint(0, 15) == 0:
                    self.add_particle()
            for p in self.particles:
                if not self.game_over:
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
                # pygame.draw.circle(self.window, 'yellow', # show the circle hitbox
                #                     (a.rect.centerx + offset, a.rect.centery + offset), a.radius)
                blit_center(self.window, pygame.transform.rotate(a.image, a.angle),
                            (a.rect.centerx + offset, a.rect.centery + offset))
                if not self.game_over:
                    a.update(self.speed, self.dt/100)
                    if a.rect.top > self.WIN_SIZE[1]+25:
                        self.asteroids.remove(a)
            
            # update and render player
            if not self.game_over:
                if self.player.update(self.dt/100):
                    self.end_game()
            self.fire.update_render(self.window, self.dt)
            # pygame.draw.rect(self.window, 'yellow', self.player.rect) # player hitbox
            blit_center(self.window, self.player.image, 
                        (self.player.rect.centerx + offset, self.player.rect.centery + offset))
            
            # render dead animation
            if self.animation:
                # circles around the collision
                pygame.draw.circle(self.window, 'white', 
                                   (self.player.rect.centerx+offset, self.player.rect.centery+offset), 
                                   circle_radius, 5)
                pygame.draw.circle(self.window, 'white', 
                                   (self.player.rect.centerx+offset, self.player.rect.centery+offset), 
                                   circle_radius/3, 3)
                # destruction effect
                for p in self.vfx_particles:
                    p.update(self.dt)
                    p.render(self.window)
                    if not p.alive:
                        self.vfx_particles.remove(p)
            
            # indications
            self.window.blit(self.time_font.render(str(self.current_time), True, 'green'), (10, 10))
            if self.game_over and not self.animation:
                self.window.blit(self.game_over_msg, self.game_over_msg_pos)
                self.window.blit(self.time_msg, self.time_msg_pos)
                self.window.blit(self.time_passed, self.time_passed_pos)
            
            pygame.display.flip()


try:
    game = Game()
    game.run()
except Exception as crash:
    pygame.quit()
    raise crash
