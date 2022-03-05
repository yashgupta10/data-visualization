# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 22:59:34 2020

@author: yashm
"""


from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from epollchain.config import Config


#db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    # create and configure the app
    app = Flask(__name__) #instance_relative_config=True)
    app.config.from_object(Config)

    #db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'

#    from . import chain
#    app.register_blueprint(chain.bp,url_prefix='/chain', url_defaults={'url_prefix': 'chain'})
#
#    from . import blockchain
#    app.register_blueprint(blockchain.bp)
#    
#    from . import forms
#    app.register_blueprint(forms.bp)
#    
#    return app


    from epollchain.users.routes import users
    from epollchain.chain.routes import chain
    #from Blockvote.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(chain,url_prefix='/', url_defaults={'url_prefix': ''})#,url_prefix='/chain', url_defaults={'url_prefix': 'chain'})
    #app.register_blueprint(main)

    return app