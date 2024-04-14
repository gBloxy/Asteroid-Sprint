
import pygame

import scripts.core as c


hidden_icon = pygame.transform.scale(pygame.image.load('asset\\success\\hidden.png'), (56, 56))
# c.swipe_color(hidden_icon, 'black', 'cyan')


class Success():
    def __init__(self, id, title, description, hidden=False, unlock_func=None):
        self.id = id
        self.title = title
        self.description = description
        self.icon_unlocked = pygame.image.load('asset\\success\\' + id + '.png')
        self.icon_locked = pygame.transform.grayscale(self.icon_unlocked)
        self.icon = hidden_icon if hidden else self.icon_locked
        self.hidden = hidden
        self.unlock_func = unlock_func
        self.unlocked = False
    
    def unlock(self):
        self.unlocked = True
        self.icon = self.icon_unlocked


class SuccessManager():
    def __init__(self):
        data = c.read_file('asset\\success.json')
        self.success_data, self.success_order = data['success'], data['order']
        self.success = {}
        self.unlocked = []
        
    def setup(self, unlocked):
        for s in self.success_data.keys():
            success = Success(s, *self.success_data[s])
            self.success[s] = success
            if s in unlocked:
                success.unlock()
                self.unlocked.append(s)
    
    def unlock(self, id):
        if not id in self.unlocked:
            self.unlocked.append(id)
            self.success[id].unlock()


class GameDataManager():
    def __init__(self):
        self.data_file = 'data\\data.json'
        self.success_mgr = SuccessManager()
        self.load_data()
    
    def load_data(self):
        data = c.read_file(self.data_file)
        self.high_score = data['time']
        self.credits = int(data['currency'])
        self.magnet_power = int(data['magnet'])
        self.games_nb = int(data['games_nb'])
        self.success_mgr.setup(data['unlocked_success'])
    
    def get_data(self):
        return {
            'time': self.high_score,
            'currency': str(self.credits),
            'magnet': str(self.magnet_power),
            'games_nb': str(self.games_nb),
            'unlocked_success': self.success_mgr.unlocked
            }
    
    def save_data(self):
        c.write_file(self.data_file, self.get_data())
    
    def incr_game_nb(self):
        self.games_nb += 1
    
    def check_high_score(self, score):
        if c.time_to_seconds(score) > c.time_to_seconds(self.high_score):
            self.high_score = score
            return True
        else:
            return False
    
    def set_credits(self, credits):
        self.credits += credits
    
    def get_success(self, id):
        return self.success_mgr.success[id]