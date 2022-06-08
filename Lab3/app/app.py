
import re
from flask import Flask, make_response, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


app = Flask(__name__)
application = app

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'авторизуйтесь'
login_manager.login_message_category = 'warning'


class User(UserMixin):
    def __init__(self, user_id, login, password):
        super().__init__()
        self.id = user_id
        self.login = login
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user['user_id'] == user_id:
            return User(**user)
    return None

def get_users():  
    return [{'user_id': '1', 'login': 'user', 'password': 'qwerty'}]

app.config.from_pyfile('config.py')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visits')
def visits():
    if session.get('visits_count') is None:
        session['visits_count'] = 1
    else:
        session['visits_count'] += 1
    return render_template('visits.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_ = request.form.get('login')
        password_ = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        for user in get_users():
            if user['login'] == login_ and user['password'] == password_:
                login_user(User(**user), remember=remember_me)
                flash('Классный вход', 'success')
                next_ = request.args.get('next')
                return redirect(next_ or url_for('index'))
        flash('Проверьте логин и пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret_page')
@login_required
def secret_page():
    return render_template('secret_page.html')