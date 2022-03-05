# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 02:21:39 2020

@author: yashm
"""

from epollchain import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port='5000')