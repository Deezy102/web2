from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from mysql_db import MySQL
import mysql.connector as connector
import re


app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

mysql = MySQL(app)

CREATE_PARAMS = ['login', 'password', 'first_name',
                 'last_name', 'middle_name', 'role_id']

UPDATE_PARAMS = ['first_name',
                 'last_name', 'middle_name', 'role_id']

# импорт после создания объектов тк файлы связаны
from auth import init_login_manager, bp as auth_bp, check_rights
init_login_manager(app)
app.register_blueprint(auth_bp)


def request_params(params_list):
    params = {}
    for param_name in params_list:
        params[param_name] = request.form.get(param_name) or None
    return params


def load_roles():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT id, name FROM roles;')
        roles = cursor.fetchall()
    return roles


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users')
def users():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute(
            'SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON users.role_id = roles.id;')
        users = cursor.fetchall()
    return render_template('users/index.html', users=users)


@app.route('/users/new')
@login_required
@check_rights('create')
def new():
    return render_template('users/new.html', user={}, roles=load_roles(), errors_dict={})


@app.route('/users/create', methods=['POST'])
@login_required
@check_rights('create')
def create():
    params = request_params(CREATE_PARAMS)
    params['role_id'] = int(params['role_id']) if params['role_id'] else None
    errors_dict = check_input_data(params)
    if errors_dict:
        flash('Введены некорректные данные. Ошибка сохранения', 'danger')
        return render_template('users/new.html', user=params, roles=load_roles(), errors_dict=errors_dict)
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute(
                ('INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)'
                 'VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);'),
                params
            )
            mysql.connection.commit()
        except connector.Error:
            flash('Введены некорректные данные. Ошибка сохранения', 'danger')
            return render_template('users/new.html', user=params, roles=load_roles(), errors_dict={})
    flash(f"Пользователь {params.get('login')} был успешно создан! ", 'success')
    return redirect(url_for('users'))


@app.route('/users/<int:user_id>')
@login_required
@check_rights('show')
def show(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
@login_required
@check_rights('update')
def edit(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/edit.html', user=user, roles=load_roles(), errors_dict={})


@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@check_rights('update')
def update(user_id):
    params = request_params(UPDATE_PARAMS)
    params['role_id'] = int(params['role_id']) if params['role_id'] else None
    params['id'] = user_id
    errors_dict = check_input_data(params)
    if errors_dict:
        flash('Введены некорректные данные. Ошибка сохранения', 'danger')
        return render_template('users/edit.html', user=params, roles=load_roles(), errors_dict=errors_dict)
    if not current_user.can('assign_role'):
        del params['role_id']
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute((
                f"UPDATE users SET {', '.join(['{0}=%({0})s'.format(k) for k, _ in params.items() if k != 'id' ])} "
                'WHERE id = %(id)s;'), params)
            mysql.connection.commit()
        except connector.Error:
            flash('Введены некорректные данные. Ошибка сохранения', 'danger')
            return render_template('users/edit.html', user=params, roles=load_roles(), errors_dict={})
    flash("Пользователь был успешно обновлен!", 'success')
    return redirect(url_for('show', user_id=user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights('delete')
def delete(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute(
                ('DELETE FROM users WHERE id=%s'), (user_id, ))
            mysql.connection.commit()
        except connector.Error:
            flash('Не удалось удалить пользователя', 'danger')
            return redirect(url_for('users'))
    flash("Пользователь был успешно удален!", 'success')
    return redirect(url_for('users'))


def check_input_data(params):
    # 'login', 'password', 'first_name', 'last_name', 'middle_name', 'role_id'
    error_dict = {}
    for k, v in params.items():
        if k == 'role_id':
            continue
        if v == '' or v is None and k != "middle_name":
            if k == 'password':
                error_dict[k] = ['Не может быть пустым']
                continue
            error_dict[k] = 'Не может быть пустым'
        

    if params.get('login') is not None:
        login = params.get('login')
        if not re.match(r"[A-Za-z0-9]{5,128}", login):
            error_dict['login'] = ("Логин должен состоять только из латинских букв и цифр"
                                   "и иметь длину от 5 до 128 символов")

    if params.get('password') is not None:
        password = params.get('password')
        error_dict['password'] = check_password(password=password)
        if error_dict['password'] is None:
            del error_dict['password']

    if params.get('new_password') is not None and params.get('repeated_password') is not None:
        error_dict['new_password'] = check_password(
            password=params.get('new_password'))
        if error_dict['new_password'] is None:
            del error_dict['new_password']
        if params.get('new_password') != params.get('repeated_password'):
            error_dict['repeated_password'] = 'Пароли не совпадают'

    return error_dict


def check_password(password):
    if (not re.match((r"[A-Za-z~!?@#$%^&*_\-+()[\]{}><\\/|\"'.,:;]*"
                      "\d[A-Za-z0-9~!?@#$%^&*_\-+()[\]{}><\\/|\"'.,:;]*"
                      "|[А-Яа-я~!?@#$%^&*_\-+()[\]{}><\\/|\"'.,:;]*"
                      "\d[А-Яа-я0-9~!?@#$%^&*_\-+()[\]{}><\\/|\"'.,:;]*"),
                     password)  # don't match the pattern
            or not (not password.islower()
                    and not password.isupper())  # not multi-case text
            or not 8 <= len(password) <= 128):  # len less then 8 or greater then 128
        return [
            "не менее 8 символов;",
            "не более 128 символов;",
            "как минимум одна заглавная и одна строчная буква;",
            "только латинские или кириллические буквы;",
            "как минимум одна цифра;",
            "только арабские цифры;",
            "без пробелов;",
            "допустимые символы:~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" ' . , : ;"
        ]
    else:
        return None


@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        repeated_password = request.form.get('repeated_password')
        params = {
            'old_password': old_password,
            'new_password': new_password,
            'repeated_password': repeated_password
        }
        errors_dict = check_input_data(params=params)
        print(errors_dict)
        if errors_dict:
            flash('Введены некорректные данные. Ошибка обновления пароля', 'danger')
            return render_template('change_password.html', errors_dict=errors_dict)
        with mysql.connection.cursor(named_tuple=True) as cursor:
            try:
                cursor.execute(
                    'SELECT * FROM users WHERE id=%s AND password_hash=SHA2(%s, 256);', (user_id, old_password))
                user = cursor.fetchone() or None
                print(user)
            except connector.Error:
                flash('Введены некорректные данные. Ошибка обновления пароля', 'danger')
                return render_template('change_password.html', errors_dict=errors_dict)
        if user is None:
            flash('Вы неверно ввели старый пароль', 'danger')
            return render_template('change_password.html', errors_dict={'old_password': 'Неверно введен старый пароль'})
        if user.id == user_id:
            with mysql.connection.cursor(named_tuple=True) as cursor:
                try:
                    cursor.execute(
                        'UPDATE users SET password_hash=SHA2(%s, 256) WHERE id=%s;', (new_password, user_id))
                    mysql.connection.commit()
                except connector.Error:
                    flash('Непредвиденная ошибка обновления пароля, попробуйте позже', 'danger')
                    return render_template('change_password.html', errors_dict={})
            flash("Пароль успешно обновлен!", 'success')
            return redirect(url_for('index'))
    return render_template('change_password.html', errors_dict={})

