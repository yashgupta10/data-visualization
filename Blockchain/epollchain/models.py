# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 22:40:45 2020

@author: yashm
"""
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from epollchain import login_manager#db,
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user


class User(UserMixin):

    with open('epollchain/data/personal.json') as file:
        personal = json.load(file)
    id = personal['emailid']
    username = personal['name']
    email = personal['emailid']
    #image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = personal['password']
    #posts = db.relationship('Post', backref='author', lazy=True)
    image_file = 'profile.jpg'

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
