from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    items = db.relationship('Item', backref='author', lazy='dynamic')
    groups = db.relationship('GroupMembership', backref='member', lazy='dynamic')

    def __repr__(self):
        return f'< User {self.username} >'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password_attempt):
        return check_password_hash(self.password_hash, password_attempt)
    

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __repr__(self):
        return f'<Post {self.body} Author: {self.user_id} Group: {self.group_id} >'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(300), index=True)
    time_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    items = db.relationship('Item', backref='group', lazy='dynamic')
    users = db.relationship('GroupMembership', backref='members', lazy='dynamic')

    def __repr__(self):
        return f'< Group {self.name} >'



class GroupMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    is_admin = db.Column(db.Boolean, index=True)

    def __repr__(self):
        return f'< user {self.user_id} in group {self.group_id}. Admin {self.is_admin} >'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))