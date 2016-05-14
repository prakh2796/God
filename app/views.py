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


def get_db():
    """Initializes the database."""
    db = MySQLdb.connect(DB_CONN['HOST'], DB_CONN['USERNAME'], DB_CONN['PASSWORD'], DB_CONN['DATABASE'])
    return db, db.cursor()


###########################################   Login Verification    #############################################
@app.route('/<login_user>/', methods=['POST'])
def login(login_user):
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
		return jsonify(status='success', msg='Login Successfull', username=username)
	else:
		return jsonify(status='error', error_msg='Invalid Username or Password')



###########################################   All Posts    #############################################
@app.route('/home/', methods=['GET'])
def home():
	post = []
	admin_name = []
	db,cursor = get_db()
	cursor.execute('SELECT title,content,id,admin_id FROM Post')
	for row in cursor.fetchall():
		post.append(dict({'title':row[0],'content':row[1],'id':row[2]}))
		temp = row[3]
		cursor.execute('SELECT name FROM Admin WHERE id="{0}"'.format(temp))
		entries = cursor.fetchall()
		admin_name.append(entries[0][0])
	return jsonify(status='success', post=post, admin_name=admin_name)


###########################################   Answer/Comment  #################################################
@app.route('/expand/<post_id>', methods=['GET'])
def expand(post_id):
	comment = []
	user_name = []
	db,cursor = get_db()
	cursor.execute('SELECT content,user_id FROM Comment WHERE post_id="{0}"'.format(post_id))
	for row in cursor.fetchall():
		comment.append(dict({'content':row[0]}))
		temp = row[1]
		cursor.execute('SELECT name FROM User WHERE id="{0}"'.format(temp))
		entries = cursor.fetchall()
		user_name.append(entries[0][0])
	return jsonify(status='success', comment=comment, user_name=user_name)

