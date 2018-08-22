from flask import Flask, render_template, redirect, session, request, flash
from mysqconnection import MySQLConnector

app = Flask(__name__)

app.secret_key = "a;dfksjladwfopahwefhjkl;"
db = MySQLConnector(app, 'remind_demo')

@app.route('/')
def index():
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
  if len(request.form['email']) < 3:
    flash('Email must be at least 3 characters')
    errors = True

  if errors == True:
    return redirect('/new')
  else:
    # MAKE SURE EMAIL IS UNIQUE
    insert_query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES(:first_name, :last_name, :email, NOW(), NOW())"
    form_data = {
      "first_name": request.form['first_name'],
      "last_name": request.form['last_name'],
      "email": request.form['email']
    }
    db.query_db(insert_query, form_data)
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
  return redirect('/')

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
  return render_template('show.html', user=user)

@app.route('/cheat-sheet')
def cheat_sheet():
  return render_template('restful-routes.html')

app.run(debug = True)

