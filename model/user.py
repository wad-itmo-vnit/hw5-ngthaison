import random
import string
import app_config
from werkzeug.security import generate_password_hash, check_password_hash

def gen_session_token(length=24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return token

class User:
    def __init__(self, username, password, token=None):
        self.username = username
        self.password = password
        self.token = token
        self.dump()
    
    @classmethod
    def new(cls, username, password):
        password = generate_password_hash(password)
        return cls(username, password)

    classmethod
    def from_file(cls, filename):
        with open(app_config.USER_DB_DIR + '/' + filename, 'r') as f:
            text = f.readline().strip()
            username, password, token = text.split(';')
            if token == 'None':
                return cls(username, password)
            return cls(username, password, token)

    def authenticate(self, password):
        return check_password_hash(self.password, password)

    def init_session(self):
        self.token = gen_session_token()
        return self.token
        self.dump()

    def authorize(self, token):
        return token == self.token

    def terminate_session(self):
        self.token = None
        self.dump()

    def __str__(self):
        return f'{self.username};{self.password};{self.token}'

    def dump(self):
        with open(app_config.USER_DB_DIR + '/' + self.username + '.data', 'w') as f:
            f.write(str(self))