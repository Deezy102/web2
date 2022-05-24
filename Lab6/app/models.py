from flask_login import UserMixin
from app import db
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash


class Category(db.Model):
    __tablename__ = 'categories' #по умолчанию название как у класса, если не нрав, то можно поменять так
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    # метод для вывода в консоль
    def __repr__(self):
        return '<Category %r>' % self.username
    
class User(db.Model, UserMixin):
    __tablename__ = 'web_users'

    id = db.Column(db.Integer, primary_key = True)
    last_name = db.Column(db.String(100), nullable = False)
    first_name = db.Column(db.String(100), nullable = False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, server_default = sa.sql.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    def __repr__(self):
        return '<User %r>' % self.login