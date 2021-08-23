from flask import Flask, render_template, request, redirect, make_response, flash
from functools import wraps
from model.user import User
import app_config
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = app_config.SECRET_KEY

# users = {}
# users['admin'] = User('admin', 'admin')

users = {name[:-5]:User.from_file(name) for name in os.listdir(app_config.USER_DB_DIR)}

def generate_token(user, pwd):
    return user + ":" + pwd

def login_required(func):
    @wraps(func)
    def login_func(*arg, **kwargs):
        try:
            if (users[request.cookies.get('username')].authorize(request.cookies.get('token'))):
                return func(*arg, **kwargs)
        except:
            pass
        flash("Login required!")
        return redirect('/login')
    return login_func

def no_login(func):
    @wraps(func)
    def no_login_func(*arg, **kwargs):
        try:
            if (users[request.cookies.get('username')].authorize(request.cookies.get('token'))):
                flash("You've already logged in!")
                return redirect('/index')
        except:
            pass
        return func(*arg, **kwargs)
    return no_login_func

# Home route - always redirect to login
@app.route('/')
def home():
    return redirect('/index')

@app.route('/login', methods=['GET', 'POST'])
@no_login
def login():
    if request.method =='GET':
        return render_template('login.html')
    user = request.form.get('username')
    pwd = request.form.get('password')
    if user in users.keys():
        current_user = users[user]
        if users[user].authenticate(pwd):
            token = users[user].init_session()
            resp = make_response(redirect('/index'))
            resp.set_cookie('username', user)
            resp.set_cookie('token', token)
            return resp
        else:
            flash("Username or password is incorrect!")
    else:
        flash("Username or password is incorrect!")
    
    return render_template('login.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    username = request.cookies.get('username')
    users[username].terminate_session()
    resp = make_response(redirect('/login'))
    resp.delete_cookie('username')
    resp.delete_cookie('token')
    flash("You've logged out!")
    return resp

@app.route('/register', methods=['POST', 'GET'])
@no_login
def register():
    if request.method == "GET":
        return render_template('register.html')

    username, password, password_confirm = request.form.get('username'), request.form.get('password'), request.form.get('password_confirm')

    if username not in users.keys():
        if password == password_confirm:
            users[username] = User.new(username, password)
            token = users[username].init_session()
            resp = make_response(redirect('/index'))
            resp.set_cookie('username', username)
            resp.set_cookie('token', token) 
            return resp
        else:
            flash("Passwords don't match!")
    else:
        flash("User already exists!")

    return render_template('register.html')
     
if __name__ == '__main__':
    app.run(host='localhost', port='5000', debug=True)
