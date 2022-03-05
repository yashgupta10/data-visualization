# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 18:38:33 2020

@author: yashm
"""
import json
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from epollchain.models import User
from flask import request
import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests

class PollForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Poll Question', validators=[DataRequired()])
    submit = SubmitField('Post to start voting')
    
class VoteForm(FlaskForm):
    transaction_detail = StringField('transaction_detail', validators=[DataRequired()])
    vote_value = RadioField('Please vote', choices=[('Yes','Yes'),('No','No')],validators=[DataRequired()])
    submit = SubmitField('Vote')
    
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0',transaction_id=None)
        self.nodes = set()
        self.active = "Active"
    
    def create_block(self, proof, previous_hash,transaction_id):
        block = {'index': len(self.chain) + 1,
                         'timestamp': str(datetime.datetime.now()),
                         'proof': proof,
                         'previous_hash': previous_hash,
                         'transactions': None}
        for transaction in self.transactions:
            if str(transaction_id)== str(transaction['transaction_id']):
                block = {'index': len(self.chain) + 1,
                         'timestamp': str(datetime.datetime.now()),
                         'proof': proof,
                         'previous_hash': previous_hash,
                         'transactions': transaction}
                self.transactions.remove(transaction)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
#        check_proof = False
#        while check_proof is False:
#            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
#            if hash_operation[:4] == '0000':
#                check_proof = True
#            else:
#                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]       
            if not(str(block['previous_hash']) == str(self.hash(previous_block))):
                return False
#            previous_proof = previous_block['proof']
#            proof = block['proof']
#            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
#            if hash_operation[:4] != '0000':
#                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, question_title,question, posted_by, time_posted, vote, voter,time_voted):
        parsed_url = urlparse(request.host_url)
        parsed_url=  hashlib.sha256(parsed_url.netloc.encode()).hexdigest()
        transaction_id = str(parsed_url)+'TT_ID:'+str(len(self.transactions))
        self.transactions.append({'transaction_id':transaction_id,
                                  'question_title':question_title,
                                  'question': question,
                                  'posted_by':posted_by,
                                  'time_posted':time_posted,
                                  'vote': vote,
                                  'voter': voter,
                                  'time_voted':time_voted})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        print("gg",address)
        parsed_url = urlparse(address)
        self.nodes.add(address)#parsed_url.netloc
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            print (f'http://{node}/get_chain')
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                print(length,max_length,chain)
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False