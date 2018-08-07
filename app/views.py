from app import app, db, lm, oid
from flask import render_template, flash, redirect, g, url_for, session, request
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, EditForm
from .models import User
from datetime import datetime
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index/')
@login_required
def index():
    # user = {'nickname':'Miguel'}
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('./index.html', title='Home', user=user, posts=posts)

@app.route('/login/', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    print('0000')
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        '''
        flash('Login requested for OpenID=' + form.openid.data + ', remember_me= ' + str(form.remeber_me.data))
        session['remember_me'] = form.remeber_me.data
        
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        '''
        print('1111')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    print('2222')
    return render_template('./login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'])


@lm.user_loader
def user_loader(id):
    return User.query.get(int(id))

@oid.after_login
def after_login(resp):
    print('3333')
    if resp.email is None or resp.email == '':
        flash('Invalid login. Plase try again')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == '':
            nickname = resp.email.split('@')[0]
        user = User(nick_name=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user=user, remember=remember_me)
    print('1111111111')
    return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('Nick '+ nickname + ' Not Found')
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('./user.html', user=user, posts=posts)

@app.route('/edit', methods=['POST', 'GET'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your Changes have been saves')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('./edit.html', form=form)