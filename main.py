from flask import Flask, render_template, request, redirect, make_response, flash
from functools import wraps
from model.user import User
import app_config

app = Flask(__name__)
app.config['SECRET_KEY'] = app_config.SECRET_KEY

def check_cookie(req):
    return User.get_user(req.cookies.get('username')).authorize(req.cookies.get('token')) 

def login_required(func):
    @wraps(func)
    def login_func(*arg, **kwargs):
        try:
            if check_cookie(request):
                print('asd')
                return func(*arg, **kwargs)
        except:
            pass
        print('asdd')
        print(request.cookies.get('username'))
        print(request.cookies.get('token'))
        flash("Login required!")
        return redirect('/login')
    return login_func

def no_login(func):
    @wraps(func)
    def no_login_func(*arg, **kwargs):
        try:
            if check_cookie(request):
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
    if User.find_user(user): 
        current_user = User.get_user(user)
        if current_user.authenticate(pwd):
            token = current_user.init_session()
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
    current_user = User.get_user(username)
    current_user.terminate_session()
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

    if not User.find_user(username):
        if password == password_confirm:
            new_user = User.new(username, password)
            token = new_user.init_session()
            resp = make_response(redirect('/index'))
            resp.set_cookie('username', username)
            resp.set_cookie('token', token) 
            return resp
        else:
            flash("Passwords don't match!")
    else:
        flash("User already exists!")

    return render_template('register.html')

@app.route('/changepwd', methods=['POST', 'GET'])
@login_required
def changepwd():
    if request.method == "GET":
        return render_template("changepwd.html")

    username = request.cookies.get("username")
    old_pwd = request.form.get('old_pwd')
    new_pwd = request.form.get('new_pwd')
    new_pwd_confirm = request.form.get('new_pwd_confirm')

    current_user = User.get_user(username)
    if current_user.authenticate(old_pwd):
        if new_pwd == new_pwd_confirm:
            current_user.update_password(new_pwd)
            flash("Password updated successfully!")
            return redirect('/')
        else:
            flash("New passwords don't match")
    else:
        flash("Old password is not correct!")
    return render_template("changepwd.html")

if __name__ == '__main__':
    app.run(host='localhost', port='5000', debug=True)
