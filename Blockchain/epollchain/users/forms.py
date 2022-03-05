# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 18:34:41 2020

@author: yashm
"""


import json
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from epollchain.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    remember = BooleanField('Remember Me')
    
    def validate_username(self, username):
        with open('epollchain/data/personal.json') as file:
            personal = json.load(file)
        if username == personal['name']:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        with open('epollchain/data/personal.json') as file:
            personal = json.load(file)
        if email == personal['emailid']:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            with open('epollchain/data/personal.json') as file:
                personal = json.load(file)
            if username == personal['name']:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            with open('epollchain/data/personal.json') as file:
                personal = json.load(file)
            if email == personal['emailid']:
                raise ValidationError('That email is taken. Please choose a different one.')