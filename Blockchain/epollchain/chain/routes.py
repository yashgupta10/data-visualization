# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 23:20:06 2020

@author: yashm
"""

import functools
from flask_bcrypt import Bcrypt
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
import requests
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
from epollchain.chain.blockchain import (Blockchain,PollForm,VoteForm)
 

chain = Blueprint('chain', __name__,url_prefix='/')

#bp = Blueprint('chain', __name__, url_prefix='/chain')

@chain.url_defaults
def bp_url_defaults(endpoint, values):
    url_prefix = getattr(g, 'url_prefix', None)
    if url_prefix is not None:
        values.setdefault('url_prefix', url_prefix)

@chain.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = values.pop('url_prefix')
    
    

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

#Create bcrypt object
bcrypt = Bcrypt()


@chain.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,'length': len(blockchain.chain)}
    return jsonify(response),200#jsonify(response), 200


@chain.route('/show_chain', methods = ['GET'])
@login_required
def show_chain():
    replace_chain = blockchain.replace_chain()
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    print('valddd',is_valid)
    if is_valid and replace_chain:
        valid = 'Replaced and Validated'
    elif is_valid and not replace_chain:
        valid = 'Validated'
    else:
        valid = 'Invalid'
        
    return render_template('show_chain.html',res_chain=blockchain.chain,valid=valid)#jsonify(response), 200

# Connecting new nodes
@chain.route('/home', methods = ['GET'])
@login_required
def connect_node():
    with open('epollchain/data/personal.json') as file:
        personal = json.load(file)
        personal['privatekey']=blockchain.hash(personal)
        personal['publickey']=blockchain.hash(personal['privatekey'])
    print(request.host_url)
    with open('epollchain/data/nodes.json') as file:
        nodes = json.load(file)
    if nodes == {}:
         nodes = {'message': 'Not connected.'}
    else:
        for node in nodes:
            try:
                print (f'http://{node}/isactive')
                if ((requests.get(f'http://{node}/isactive')).json()["status"] == "Active"):
                    blockchain.add_node(node)
                    requests.post(f'http://{node}/isactive',json={request.host_url:""})
            except:
                print("fail to connect")
        if len(blockchain.nodes)>0:
            nodes = {'message': 'All the nodes are now connected.','total_nodes': list(blockchain.nodes)}
        else :
            nodes = {'message': 'Not connected.'}

    return render_template('home.html',res_personal = personal, res_nodes = nodes)
                           
@chain.route('/isactive', methods = ['GET'])
def is_active():
    return jsonify({"status":blockchain.active}),200

@chain.route('/gettransaction', methods = ['GET'])
def gettransaction():
    if blockchain.transactions:
        return jsonify(blockchain.transactions,200)
    else:
        return jsonify({}),200

@chain.route('/isactive', methods = ['POST'])
def active_add():
    parsed_url = urlparse(request.get_json())
    print(parsed_url.netloc)
    with open('epollchain/data/nodes.json','w+') as outfile:
        json.dump(parsed_url.netloc, outfile)
    return "Added",200

@chain.route("/poll/new", methods=['GET', 'POST'])
@login_required
def new_poll():
    form = PollForm()
    print (current_user.email)
    if form.validate_on_submit():
        index = blockchain.add_transaction(form.title.data, form.content.data,current_user.email, str(datetime.datetime.now()),None,None,None)
        print (index,blockchain.transactions)
        flash('Your poll has been created!', 'success')
        return redirect('/mine')
    return render_template('create_poll.html', title='New Poll',
                           form=form, legend='New Poll')

@chain.route("/polls", methods=['GET', 'POST'])
def polls():
    replace_chain = blockchain.replace_chain()
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    transaction_polls=[]
    for transaction in blockchain.chain:
        print(transaction)
        if transaction['index']>1:
            if transaction['transactions']['vote']==None:
                transaction_polls.append(transaction['transactions'])
    return render_template('polls.html', transactions = transaction_polls)#return render_template('home.html', posts=posts)

@chain.route("/vote/<string:poll_id>", methods=['GET', 'POST'])
def vote(poll_id):
    pollvote={}
    form = VoteForm()
    for transaction in blockchain.chain:
        if transaction['index']>1 and str(poll_id)== str(transaction['transactions']['transaction_id']):
            pollvote=transaction['transactions']
    if request.method == 'POST' or form.validate_on_submit():
        print ('aaaaa',form.transaction_detail.data)
        index = blockchain.add_transaction(pollvote['question_title'], pollvote['question'],pollvote['posted_by'],pollvote['time_posted'],form.vote_value.data,current_user.email,str(datetime.datetime.now()))
        print (index,form.vote_value.data)
        flash('Your poll has been created!', 'success')
        return redirect('/polls')
    elif request.method == 'GET':
        form.transaction_detail = pollvote
    return render_template('vote.html', pollvote = pollvote,form = form)


@chain.route("mine", methods=['GET'])
def mine():
    with open('epollchain/data/nodes.json') as file:
        nodes = json.load(file)
    if nodes == {}:
         nodes = {'message': 'Not connected.'}
    else:
        for node in nodes:
            try:
                if ((requests.get(f'http://{node}/gettransaction')).json()):
                    new_t = (requests.get(f'http://{node}/gettransaction')).json()
                    print (new_t[0])
                    for transaction in new_t[0]:
                        for local_transaction in blockchain.transactions:
                            if not(transaction['transaction_id']==local_transaction['transaction_id']):
                                blockchain.transactions.append(transaction)
            except requests.ConnectionError:
                print("fail to connect")
    return render_template('mine.html', transactions = blockchain.transactions)

@chain.route("/mine/<string:transaction_id>", methods=['GET', 'POST'])
def block(transaction_id):
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash,transaction_id)
    print(block)
    flash('Your block has been created!', 'success')
    return render_template('mine.html', transactions = blockchain.transactions)


