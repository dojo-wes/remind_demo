from flask import Flask, render_template, redirect, session, request, flash
from mysqconnection import MySQLConnector
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = "a;dfksjladwfopahwefhjkl;"
db = MySQLConnector(app, 'remind_demo')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/new')

  query = 'SELECT * FROM users'
  users_list = db.query_db(query)
  return render_template('index.html', users=users_list)

@app.route('/create', methods=['POST'])
def create():
  errors = False

  # define validations
  if len(request.form['first_name']) < 3:
    flash('First name must be at least 3 characters long.')
    errors = True
  if len(request.form['last_name']) < 3:
    flash('Last name must be at least 3 characters')
    errors = True
  if not EMAIL_REGEX.match(request.form['email']):
    flash('Email must be valid')
    errors = True
  # validate that password is at least 8 chars
  if len(request.form['password']) < 8:
    flash('Password must be at least 8 characters long')
    errors = True
  # validate that password and confirm match
  if request.form['password'] != request.form['confirm']:
    flash('Confirm password must match password')
    errors = True

  if errors == True:
    return redirect('/new')
  else:
    # validate that email does not already exist in db
    email_query = 'SELECT id, email FROM users WHERE email=:email'
    email_data = {
      'email': request.form['email']
    }
    result = db.query_db(email_query, email_data)
    if len(result) > 0:
      flash('Email already exists')
      return redirect('/new')

    # hash and add password to query
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES(:first_name, :last_name, :email, :password, NOW(), NOW())"
    form_data = {
      "first_name": request.form['first_name'],
      "last_name": request.form['last_name'],
      "email": request.form['email'],
      "password": pw_hash
    }
    user_id = db.query_db(insert_query, form_data)
    session['user_id'] = user_id
  return redirect('/')

@app.route('/<user_id>/update', methods=["POST"])
def update(user_id):
  # processing the update form
  errors = False
  
  if len(request.form['first_name']) < 3:
    flash('First name must be at least 3 characters long.')
    errors = True
  if len(request.form['last_name']) < 3:
    flash('Last name must be at least 3 characters')
    errors = True
  if len(request.form['email']) < 3:
    flash('Email must be at least 3 characters')
    errors = True

  if errors == True:
    return redirect('/new')
  else:
    # MAKE SURE EMAIL IS UNIQUE
    email_query = 'SELECT id, email FROM users WHERE email=:email'
    email_data = {
      'email': request.form['email']
    }
    result = db.query_db(email_query, email_data)
    if len(result) > 0:
      flash('Email already exists')
      return redirect('/new')

    insert_query = "UPDATE users SET first_name=:first_name, last_name=:last_name, email=:email, updated_at=NOW() WHERE id=:user_id"
    form_data = {
      "first_name": request.form['first_name'],
      "last_name": request.form['last_name'],
      "email": request.form['email'],
      "user_id": user_id
    }
    db.query_db(insert_query, form_data)
  return redirect('/')

@app.route('/<user_id>/delete', methods=["POST"])
def destroy(user_id):
  # processing delete form
  delete_query = "DELETE FROM users WHERE id=:user_id"
  data = {
    "user_id": user_id
  }
  db.query_db(delete_query, data)
  session.clear()
  return redirect('/new')

@app.route('/new')
def new():
  return render_template('new.html')

@app.route('/<user_id>/edit')
def edit(user_id):
  user_query = 'SELECT * FROM users WHERE id=:user_id'
  data = {
    'user_id': user_id
  }
  users_list = db.query_db(user_query, data)
  user = users_list[0]
  return render_template('edit.html', user=user)

@app.route('/<user_id>')
def show(user_id):
  user_query = 'SELECT * FROM users WHERE id=:user_id'
  data = {
    'user_id': user_id
  }
  users_list = db.query_db(user_query, data)
  user = users_list[0]

  reminder_query = 'SELECT * FROM reminders WHERE creator_id=:user_id'
  reminders = db.query_db(reminder_query, data)

  return render_template('show.html', user=user, reminder_list=reminders)

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/new')

@app.route('/login', methods=['POST'])
def login():
  email_query = 'SELECT * FROM users WHERE email=:email'
  email_data = {
    'email': request.form['email']
  }
  result = db.query_db(email_query, email_data)

  if len(result) == 0:
    flash('Email or password incorrect')
    return redirect('/new')

  user = result[0]
  if bcrypt.check_password_hash(user['password'], request.form['password']) == False:
    flash('Email or password incorrect')
    return redirect('/new')

  session['user_id'] = user['id']
  return redirect('/')

@app.route('/remind_new')
def remind_new():
  return render_template('remind_new.html')

@app.route('/remind_create', methods=['POST'])
def remind_create():
  if not 'user_id' in session:
    return redirect('/new')

  errors = False

  if len(request.form['content']) < 3:
    flash('Reminder must be at least 3 characters')
    errors = True

  if errors:
    return redirect('/remind_new')

  reminder_query = 'INSERT INTO reminders (content, remind_on_date, created_at, updated_at, creator_id) VALUES (:content, NOW(), NOW(), NOW(), :current_user_id)'
  reminder_data = {
    'content': request.form['content'],
    'current_user_id': session['user_id']
  }
  db.query_db(reminder_query, reminder_data)
  return redirect('/')

@app.route('/cheat-sheet')
def cheat_sheet():
  return render_template('restful-routes.html')

app.run(debug = True)

