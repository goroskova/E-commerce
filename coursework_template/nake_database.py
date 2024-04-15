# These line of codes does the import of the librraries needed
#you can import as many libraries as you need for the database file
from flask import Flask
from flask import render_template
import sqlite3

#this line create the database with the name coursework_project. You can changey
#the name to any name of your choice. You may add as many tables to this database or you may 
#create different database for each table
con = sqlite3.connect('coursework_project.db')
try:
  #this line of code connect the database and create the table named "users"
    con.execute('CREATE TABLE users (name TEXT, pwd TEXT)')
    
    #con.execute('CREATE TABLE users (user_id INT AUTO-INCREMENT, name TEXT, pwd TEXT)')
    #print ('Table created successfully');
except:
  pass

  con.close()

