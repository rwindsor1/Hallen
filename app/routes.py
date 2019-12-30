'''
    TODO:
    Add functionality to:
        2. Add/Remove Users from Groups
        4. Deploy to Linux server/Heroku
'''

from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegisterForm, CreateGroupForm, CreatePostForm
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Item, GroupMembership, Group
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')

def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    memberships = current_user.groups.all()
    groups = [Group.query.get(membership.group_id) for membership in memberships]
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
    return render_template('index.html', title='Home', user=user, items=items, groups = groups)

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
        if 'next' in request.args:
            next_page = request.args['next']
        else:
            next_page = False
        print(f'Next page: {next_page}')
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

@app.route('/create-group', methods=['GET', 'POST'])
@login_required
def create_group():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = CreateGroupForm()
    
    if form.validate_on_submit():
        group = Group(name=form.groupname.data, description=form.groupname.data)
        db.session.add(group)
        db.session.commit()
        membership = GroupMembership(user_id = current_user.id, group_id = group.id, is_admin=True)
        db.session.add(membership)
        db.session.commit()
        flash('Group Sucessfully Created!')
        return redirect(url_for('index'))
    return render_template('create_group.html', title = 'Create Group for Hallen', form = form)
        
@app.route('/group/<groupid>')
@login_required
def group(groupid):
    group = Group.query.filter_by(id=groupid).first_or_404()
    if group.users.filter_by(user_id = current_user.id).first() is None:
        # TODO: Only render template if user is a member of the group
        flash("You don't have permissions to view this group! Contact the Group Admin to add you.")
        return redirect(url_for('index'))
    items = group.items.all()
    member_ids = [member.user_id for member in group.users.all()]
    users = []
    
    for member_id in member_ids:
        users.append(User.query.get(member_id))

    return render_template('group.html', title = f'{group.name}', group=group, items=items, users=users)

@app.route('/create-post/<groupid>-<userid>', methods=['GET', 'POST'])
@login_required
def make_post(groupid, userid):
    group = Group.query.filter_by(id=groupid).first_or_404()
    if group.users.filter_by(user_id = current_user.id).first() is None:
        # TODO: Only render template if user is a member of the group
        flash("You don't have permissions to view this group! Contact the Group Admin to add you.")
        return redirect(url_for('index'))
    form = CreatePostForm()
    if form.validate_on_submit():
        item = Item(body = form.postcontent.data, user_id = current_user.id, group_id = group.id)
        db.session.add(item)
        db.session.commit()
        return redirect('/group/{}'.format(group.id))

    return render_template('create_post.html', title = f'Create post in {group.name}', group = group, form = form)

@app.route('/edit-post/<postid>', methods=['GET','POST'])
@login_required
def edit_post(postid):
    item = Item.query.filter_by(id=postid).first_or_404()
    group = item.group
    if group.users.filter_by(user_id = current_user.id).first() is None:
        # TODO: Only render template if user is a member of the group
        flash("You don't have permissions to view this group! Contact the Group Admin to add you.")
        return redirect(url_for('index'))
    form = CreatePostForm()
    if form.validate_on_submit():
        Item.query.filter_by(id=postid).first().body = form.postcontent.data
        Item.query.filter_by(id=postid).first().user_id = current_user.id
        db.session.commit()
        return redirect(url_for('group', groupid = group.id))
    return render_template('edit_post.html', title = f'Edit post in {group.name}', group = group, form = form, item = item)

@app.route('/delete-post/<postid>', methods=['GET','POST'])
@login_required
def delete_post(postid):
    item = Item.query.filter_by(id=postid).first_or_404()
    group = item.group
    if group.users.filter_by(user_id = current_user.id).first() is None:
        # TODO: Only render template if user is a member of the group
        flash("You don't have permissions to view this group! Contact the Group Admin to add you.")
        return redirect(url_for('index'))
    item = Item.query.filter_by(id=postid).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('group', groupid = group.id))

@app.route('/confirm-delete-group/<groupid>')
@login_required
def confirm_delete_group(groupid):
    group = Group.query.filter_by(id = groupid).first_or_404()
    member = GroupMembership.query.filter_by(group_id = groupid, user_id = current_user.id).first_or_404()
    if member.is_admin:
        return render_template('delete_group.html', group = group)
    else:
        flash("You need to be a group admin to do this!;")
        return redirect(url_for('group', groupid = group.id))

@app.route('/delete-group/<groupid>', methods=['GET', 'POST'])
@login_required
def delete_group(groupid):
    group = Group.query.filter_by(id = groupid).first_or_404()
    member = GroupMembership.query.filter_by(user_id = current_user.id, 
                                             group_id = group.id).first_or_404()
    if not member.is_admin:
        flash(" You aren't an administrator of this group so you can't do that!")
        return redirect(url_for('group', groupid = group.id))

    else:
        Item.query.filter_by(group_id = groupid).delete()
        GroupMembership.query.filter_by(group_id = group.id).delete()
        Group.query.filter_by(id = groupid).delete()
        db.session.commit()
        return redirect(url_for('index'))