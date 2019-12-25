from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegisterForm
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Item
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username':'Rhydian'}
    items = [
        {
            'author': {'username': 'Rhydian'},
            'body': 'Buy more coffee'
        },
        {
            'author': {'username': 'Lizzie'},
            'body': 'Buy more teabags'
        }
    ]
    return render_template('index.html', title='Home', user=user, items=items)

@app.route('/lizzie')
def lizzie():
    return "Hello little face"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # come here if no user is entered or if password doesn't match username
            flash('Invalid Username/Password')
            return redirect(url_for('login'))
        login_user(user, remember= form.remember_me.data)
        # navigate to queued next page if in url
        next_page = request.args['next']
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logoff')
def logoff():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration Sucessfully Completed!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register for Hallen', form=form)