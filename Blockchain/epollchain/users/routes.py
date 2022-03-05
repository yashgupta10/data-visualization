# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 22:33:34 2020

@author: yashm
"""
from flask import current_app as app
import secrets
import os
from PIL import Image
import json
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from epollchain import bcrypt # db
from epollchain.models import User#, Post
from epollchain.users.forms import (RegistrationForm, LoginForm , UpdateAccountForm)#,RequestResetForm, ResetPasswordForm)
#from Blockvote.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)
user = User()


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\profile_pics', picture_fn)
 #   form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        personal = {}
        personal['name'] = form.username.data
        personal['password']=hashed_password
        personal['emailid']=form.email.data
        with open('epollchain/data/personal.json','w') as outfile:
            json.dump(personal, outfile)#json.dumps(data)
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')  
    form = LoginForm()
    with open('epollchain/data/personal.json') as file:
        personal = json.load(file)
    if form.validate_on_submit():
        if form.email.data == personal['emailid'] and bcrypt.check_password_hash(personal['password'], form.password.data):
            flash('You have been logged in!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/home')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect('/login')


@users.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
       # db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect('/account')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



