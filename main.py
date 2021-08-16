from flask import Flask, render_template, request, redirect, make_response
from functools import wraps

app = Flask(__name__)

def generate_token(user, pwd):
    return user + ":" + pwd

# Home route - always redirect to login
@app.route('/')
def home():
    return redirect('/login'), 301

def auth(request):
    token = request.cookies.get('login-info')
    try:
        user, pwd = token.split(':')
    except:
        return False
    return (user == 'admin' and pwd == 'admin')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    else:
        user = request.form.get('username')
        pwd = request.form.get('password')
        if (user == 'admin' and pwd == 'admin'):
            token = generate_token(user, pwd)
            resp = make_response(redirect('/index'))
            resp.set_cookie('login-info', token)
            return resp
        else:
            return redirect('/login'), 403

def auth_required(f):
    @wraps(f)
    def check(*arg, **kwargs):
        if auth(request):
            return render_template('index.html')
        else:
            return redirect('/')
    return check

@app.route('/index', methods=['GET', 'POST'])
@auth_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='localhost', port='5000', debug=True)
