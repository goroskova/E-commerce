from flask import Flask
from markupsafe import escape
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import make_response
import sqlite3

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    return do_the_registration(request.form['uname'], request.form['pwd'])
  else:
    return show_the_registration_form();
    
#Add this code to define the function in the else case above:    
def show_the_registration_form():
   return render_template('register.html',page=url_for('register'))

#Now add thjs function called by register(), do_the_registration(u,p)
def do_the_registration(u,p):
  
   #this line of code connect to the coursework_project database created in my_database.py file
  con = sqlite3.connect('coursework_project.db')

  '''This line of code is used to insert variable usernames and passwords into the user table created 
  in the coursework_project database of the  my_database.py file'''
  con.execute("INSERT INTO users values(?,?);", (u, p))
  con.commit()
  con.close()
   
   #IF THE REGISTRATION IS SUCCESSFUL SHOWS THE LOGIN FORM
  return show_the_login_form()

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    return do_the_login(request.form['uname'], request.form['pwd'])
  else:
    return show_the_login_form()

'''Again the main login function refers to two other functions. Here they are – integrate 
them in a suitable place: '''
def show_the_login_form():
  return render_template('login.html',page=url_for('login'))

def do_the_login(u,p):
  con = sqlite3.connect('coursework_project.db')
  cur = con.cursor()
  cur.execute("SELECT count(*) FROM users WHERE name=? AND pwd=?;", (u, p))
  if(int(cur.fetchone()[0]))>0:
    return f'<H1>Success!</H1>'
  else:
    abort(403) 

@app.errorhandler(403)
def wrong_details(error):
  return render_template('wrong_details.html'), 403

  

  
      

