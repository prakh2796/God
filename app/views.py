from app import app
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import json
import requests
from bs4 import BeautifulSoup
import MySQLdb
import inspect
import time
import MySQLdb.cursors
from settings import *
from werkzeug.security import generate_password_hash, \
     check_password_hash



def get_db():
    """Initializes the database."""
    db = MySQLdb.connect(DB_CONN['HOST'], DB_CONN['USERNAME'], DB_CONN['PASSWORD'], DB_CONN['DATABASE'])
    return db, db.cursor()

# class User(object):

#     def __init__(self, username, password):
#         self.username = username
#         self.set_password(password)

#     def set_password(self, password):
#         self.pw_hash = generate_password_hash(password)

#     def check_password(self, password):
#     	return check_password_hash(self.pw_hash, password)


###########################################   Login Verification    #############################################
@app.route('/<login_user>/', methods=['POST'])
def login(login_user):
	flag = 0
	db,cursor = get_db()
	request.form = json.loads(request.data)
	email = request.form['email']
	password = request.form['password']
	if login_user == 'Admin':
		cursor.execute('SELECT name,count(*) FROM Admin WHERE email="{0}" AND password="{1}"'.format(email,password))
	elif login_user == 'User':
		cursor.execute('SELECT name,count(*) FROM User WHERE email="{0}" AND password="{1}"'.format(email,password))
	entries = cursor.fetchall()
	username = entries[0][0]
	count = entries[0][1]
	if count > 0:
		if email == 'super@gmail.com':
			flag = 1
		return jsonify(status='success', msg='Login Successfull', username=username, flag=flag)
	else:
		return jsonify(status='error', error_msg='Invalid Username or Password')



##################################################   Signup    ################################################
@app.route('/signup', methods=['POST'])
def signup ():
	db,cursor=get_db()
	request.form = json.loads(request.data)
	email = request.form['email']
	password = request.form['password']
	username = request.form['username']
	cursor.execute('SELECT count(*) FROM User WHERE email="{0}"'.format(email))
	entries = cursor.fetchall()
	count=entries[0][0]
	
	if count == 0:
		cursor.execute('INSERT INTO user VALUES (DEFAULT,"{0}","{1}","{2}")'.format(username,email,password))
		db.commit()
		return jsonify(status='success', msg='Signup Successfull')
	else:
		return jsonify(status='error', msg='Email Already Exists !')



###########################################   All Posts    #############################################
@app.route('/home/', methods=['GET'])
def home():
	post = []
	admin_name = []
	comment_count = []
	count = 0
	db,cursor = get_db()
	cursor.execute('SELECT title,content,id,admin_id FROM Post')
	for row in cursor.fetchall():
		count = count + 1
		post.append(dict({'title':row[0],'content':row[1],'id':row[2]}))
		temp = row[3]
		cursor.execute('SELECT name FROM Admin WHERE id="{0}"'.format(temp))
		entries = cursor.fetchall()
		admin_name.append(entries[0][0])
		temp = row[2]
		cursor.execute('SELECT count(*) FROM Comment WHERE post_id="{0}"'.format(temp))
		entries = cursor.fetchall()
		comment_count.append(entries[0][0])
	return jsonify(status='success', post=post, admin_name=admin_name, count=count, comment_count=comment_count)


##################################################   Expand  #################################################
@app.route('/expand/<post_id>', methods=['GET'])
def expand(post_id):
	comment = []
	user_name = []
	count = 0
	db,cursor = get_db()
	cursor.execute('SELECT content,user_id FROM Comment WHERE post_id="{0}"'.format(post_id))
	for row in cursor.fetchall():
		count = count + 1
		comment.append(dict({'content':row[0]}))
		temp = row[1]
		cursor.execute('SELECT name FROM User WHERE id="{0}"'.format(temp))
		entries = cursor.fetchall()
		user_name.append(entries[0][0])
	return jsonify(status='success', comment=comment, user_name=user_name, count=count)

