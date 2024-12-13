
import threading
import requests
from json import load, dump
from re import compile, match
from cryptography.fernet import Fernet


class Client():
    def __init__(self, game):
        self.game = game
        
        # load config
        
        with open('asset/config.json') as file:
            self.config = load(file)
            self.url = self.config['URL']
            self.regex = compile(self.config['REGEX'])
        
        # server connection test
        
        try:
            responce = requests.get(self.url+'/get/'+self.game)
            data = responce.json()
            if 'error' in data:
                self.connected = False
            else:
                self.connected = True
        
        except Exception as error:
            print(error)
            self.connected = False
        
        print('connected :', self.connected)
        
        # load player data / check if registred
        
        with open('asset/data.json') as file:
            data = load(file)
            self.uuid = data['uuid']
            self.username = data['username']
            if self.uuid is None or not self.isValidName(self.username):
                self.username = None
                self.registred = False
            else:
                self.registred = True
        
        print('registred :', self.registred)
    
    def thread(self, func, args=tuple()):
        print('starting client thread func')
        thread = threading.Thread(target=func, args=args)
        thread.start()
    
    def isValidName(self, string):
        return bool(match(self.regex, string))
    
    def save(self):
        with open('asset/data.json', 'w') as file:
            dump({'uuid': self.uuid, 'username': self.username}, file)
    
    def register(self, username, registred=False):
        print('registering')
        if self.connected:
            if self.isValidName(username):
                responce = requests.post(
                    url  = self.config['URL_ROOT'] + '/register',
                    json = {
                        'username': username,
                        'uuid': self.uuid if registred else None,
                        'key': Fernet(b'b8eo6lOvOFWpk8JjYlGEK_dw2MULYsXhdsHrF3C5sY4=').decrypt(self.config['ACCESS_KEY']).decode()
                    }
                )
                print(responce.text)
                data = responce.json()
                if 'error' in data:
                    print(data)
                    return data
                else:
                    if not registred:
                        self.uuid = data['uuid']
                        self.registred = True
                        print('registred')
                    self.username = username
                    print('username changed')
                    self.save()
                    return {}
            else:
                return {'error': 'invalid username'}
        else:
            return {'error': 'not connected to server'}
    
    def setUsername(self, username):
        print('changing username')
        if username != self.username:
            return self.register(username, registred=True)
        return {}
    
    def getMinScore(self):
        print('getting high score')
        if self.connected:
            payload = 'mode=high:'+self.username if self.registred else 'mode=high'
            responce = requests.get(self.url+'/get/'+self.game+'?'+payload)
            return int(responce.text)
    
    def sendScore(self, score):
        print('sending score')
        if self.connected and self.registred and type(score) == int:
            data = {
                'uuid': self.uuid,
                'score': score,
                'key': Fernet(b'b8eo6lOvOFWpk8JjYlGEK_dw2MULYsXhdsHrF3C5sY4=').decrypt(self.config['ACCESS_KEY']).decode()
                }
            responce = requests.post(self.url+'/edit/'+self.game, json=data)
            data = responce.json()
            if 'error' in data:
                print(data)
                return data['error']
            print('score submitted successfuly')
