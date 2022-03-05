# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 02:16:33 2020

@author: yashm
"""
from flask import Flask, jsonify, request
import functools
import requests
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
def hash(block):
    encoded_block = json.dumps(block, sort_keys = True).encode()
    return hashlib.sha256(encoded_block).hexdigest()
with open('data/personal.json') as file:
 d = json.load(file)
 print(d["name"])
 print( hash(d))
 
address = "http://127.0.0.1:5000/"
parsed_url = urlparse(address)
print(parsed_url)
print(parsed_url.netloc)

print(hashlib.sha224(parsed_url.netloc.encode()).hexdigest())
block={'index': 2, 'timestamp': '2020-02-07 03:07:09.214215', 'proof': 1, 'previous_hash': '0b2f754b54afbabb256a32133cbcc2673fe4c1882252299445625f235f74cb38', 'transactions': {'transaction_id': 0, 'question_title': 'kh,k', 'question': ',k,', 'posted_by': 'yash.gupta@blockvote.com', 'time_posted': '2020-02-07 03:06:46.203111', 'vote': None, 'voter': None, 'time_voted': None}}

transactions = [{'transaction_id': 'http://127.0.0.1:5000/TT_ID:0', 'question_title': 'x', 'question': 'x', 'posted_by': 'yash.gupta@blockvote.com', 'time_posted': '2020-02-08 14:48:41.751512', 'vote': None, 'voter': None, 'time_voted': None}, {'transaction_id': 'http://127.0.0.1:5000/TT_ID:1', 'question_title': 'asd', 'question': 'asd', 'posted_by': 'yash.gupta@blockvote.com', 'time_posted': '2020-02-08 14:49:18.232836', 'vote': None, 'voter': None, 'time_voted': None}]
#print (json.dumps(transactions))
#response = requests.get(f'http://127.0.0.1:5000/get_chain')
#print(requests.get(f'http://127.0.0.1:5000/get_chain'))
print(request.host_url)
