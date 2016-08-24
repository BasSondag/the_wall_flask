from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector('wall')
app.secret_key = "shooower"
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/signup')
def sign():
	return render_template('create.html')

@app.route('/users', methods=['POST'])
def create():
	# print "bas"
	valid = True
	if len(request.form['first_name']) < 3 :
		flash('I need more than twoo letters for your First Name')
		valid = False
	if len(request.form['last_name']) < 3 :
		flash('I need more than twoo letters for your Last Name')
		valid = False
	if not EMAIL_REGEX.match(request.form['email']):
		flash('Invalid email address')
		valid = False
	if len(request.form['password']) < 8 :
		flash('I need a password longer than 8 carracters')
		valid = False
	if request.form['password'] != request.form['confirm']:
		flash('your password does not match')
		valid = False
	if valid == True:
		password = request.form['password']
		pw_hash = bcrypt.generate_password_hash(password)
		query = "INSERT INTO users (first_name, last_name, email, pw_hash, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(request.form['first_name'], request.form['last_name'], request.form['email'], pw_hash)
		# print query
		mysql.run_mysql_query(query)
		users=mysql.fetch("SELECT * from users where email='{}'".format(request.form['email']))
		session['userID'] = users[0]['id']
	 	flash('Your accout is succesfull created with:')
		return redirect('/wall')
	else:
		return redirect('/signup')	

@app.route('/wall')
def online():
	query="SELECT * FROM users where id ='{}'".format(session['userID'])
	users=mysql.fetch(query)
	query2="SELECT  users.first_name, users.last_name, messages.created_at, messages.message, messages.id FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.created_at DESC"
	messages=mysql.fetch(query2)
	query3= "SELECT  users.first_name, users.last_name, comments.created_at, comments.comment, comments.id, comments.message_id FROM users JOIN comments ON users.id = comments.user_id"
	comments=mysql.fetch(query3)
	# print messages
	print comments
	# print users[0]
	return render_template('welcome.html', users = users[0], messages = messages, comments = comments)	

@app.route('/login', methods=['POST'])
def login():
	email = request.form['email']
	password = request.form['password']
	user_query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email)
	user = mysql.fetch(user_query) # user will be returned in an array
	if not user:
		flash('need valid email adress:')
		return redirect('/')
	if bcrypt.check_password_hash(user[0]['pw_hash'], password):
		session['userID'] = user[0]['id']
		return redirect('/wall')
	else:
		flash('Wrong password, try again')
		return redirect('/')	
# route for the post and comment start
@app.route('/message', methods = ['POST'])
def messagepost():
	# print request.form['message']
	query = "INSERT INTO messages (message,created_at,updated_at,user_id)VALUES ('{}',NOW(), NOW(),'{}')".format(request.form['message'],session['userID'])
	mysql.run_mysql_query(query)
	return redirect('/wall')

@app.route('/comment', methods = ['POST'])
def commentpost():
	# print request.form['comment']
	# print request.form['message_id']
	query = "INSERT INTO comments (comment,created_at,updated_at, message_id, user_id)VALUES ('{}',NOW(), NOW(),'{}','{}')".format(request.form['comment'], request.form['message_id'],session['userID'])
	mysql.run_mysql_query(query)
	# print query
	return redirect('/wall')	

@app.route('/logout')
def reset():
	session.clear()
	return redirect('/')
app.run(debug = True)
 