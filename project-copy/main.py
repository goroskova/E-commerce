# -*- coding: utf-8 -*-
from flask import Flask
import sqlite3 
import random
from flask import flash, session, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import time 
import re

# github repository link: https://github.coventry.ac.uk/goroskovao/5009CEM-E-commerce-website.git


# connecting to the database 
con = sqlite3.connect('products.db')
# creating tabels
con.execute('CREATE TABLE IF NOT EXISTS products(id INT, name VARCHAR(255), code VARCHAR(255), image TEXT, price FLOAT, in_stock INT, manufacturer VARCHAR(50), category VARCHAR(50) )')
con.execute('CREATE TABLE IF NOT EXISTS users(firstname VARCHAR(100), lastname VARCHAR(100), email VARCHAR(255),password VARCHAR(255))')
con.execute('CREATE TABLE IF NOT EXISTS order_items(order_id INT, item_code VARCHAR(10), quantity INT)')
con.execute('CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT, order_email VARCHAR(255), order_firstname VARCHAR(100), order_lastname VARCHAR(100), transaction_number INT, total_price DOUBLE, card_number VARCHAR(20), card_name VARCHAR(100), card_date VARCHAR(10), card_cvv INT(3))')
con.execute('CREATE TABLE IF NOT EXISTS order_address(order_id INT, house_number VARCHAR(255), bill_house_number VARCHAR(255), street_name VARCHAR(255), bill_street_name VARCHAR(255), city VARCHAR(100), bill_city VARCHAR(100), country VARCHAR(100), bill_country VARCHAR(100), postcode VARCHAR(10), bill_postcode VARCHAR(10))')

# inserting data to the tables (the code is commented because data was already inserted)
#con.execute('INSERT INTO products(id, name, code, image, price, in_stock, manufacturer, category) VALUES (1, "Pixel 7 Pro 256Gb", "PRTR34", "pixel7.jpg", 949.99, 2,"google", "phone"),(2, "Galaxy S23", "GFD566", "galaxys23.jpg", 899.99, 32, "samsung", "phone"), (3, "OnePlus 11 5G", "OPGH43", "Oneplus.jpg", 799.99, 5, "oneplus" , "phone"), (4, "iPhone 14 Pro Max, 128Gb", "IPH543", "iphone.jpg", 1199.90, 10, "apple", "phone");')
#con.execute('INSERT INTO products(id, name, code, image, price, in_stock, manufacturer, category) VALUES (5, "iPad Air (M1)256Gb", "PHKT98G", "ipad.jpg", 820.90, 13, "apple", "tablet"),(6, "Fire HD Tablet 8-inch", "GFDTR6", "FireHD.jpg", 89.99, 32, "amazon" ,"tablet"), (7, "Galaxy Tab S6Lite 10.4inch", "GLSF23", "galaxytab.jpg", 290.90, 15,"samsung",  "tablet"), (8, "Redmi Pad -10.6in 64GB", "REDDMF66", "redmipad.jpg", 270.99, 10, "Xiaomi", "tablet");')
#con.execute('INSERT INTO products(id, name, code, image, price, in_stock, manufacturer, category) VALUES (9, "Apple MacBook Air M2 256GB", "GTRHF2F", "macbook.jpg", 1200.99, 10, "apple", "laptop"),(10, "ASUS Zenbook 14", "UX3402ZA", "zenbook.jpg", 889.99, 20, "asus" ,"laptop");')
#con.execute('INSERT INTO users(firstname, lastname, email, password) VALUES ("test1", "test1","test1","test1");')
#con.execute('INSERT INTO users(firstname, lastname, email, password) VALUES ("test2", "test2","Customer 1","ps8766ad137@");')
#con.execute('INSERT INTO users(firstname, lastname, email, password) VALUES ("test3", "test3","Customer 2","ps8766ad137@");')

con.commit()
con.close()  

app = Flask(__name__)
app.secret_key = "dfkjhbvkjbk4kjdfvbdfvasdscmganif"
    

# Function to process payment. 
# Works when user clicks on "PAY NOW" button after filling out the form on the checkout page
@app.route('/pay_now', methods=['GET', 'POST'])
def pay_now():
		try:
			if request.method == 'POST':
				# checks if form was posted successfully and connects to the database
					con = sqlite3.connect('products.db')
					cur = con.cursor()

                    # get firstname, lastname and email from the checkout form (if a user wants to checkout as a guest)
					if 'checkout_as_guest' in session:
						firstname = request.form['firstname']
						lastname = request.form['lastname']
						user_email = request.form['email']
						if payNow_data_validation(firstname,lastname, user_email) != True:
							return payNow_data_validation(firstname,lastname, user_email )

					# or get the data from existing user's account (if a user was logged in)
					else:
						user_email = session['user']
						cur.execute("SELECT firstname, lastname FROM users WHERE email=?;", [user_email])
						row = cur.fetchone()
						firstname = row[0]
						lastname = row[1]

                    # get the rest of the data from the checkout form
					house_number = request.form['house_number']
					street_name = request.form['street_name']
					city = request.form['city']
					country = request.form['country']
					postcode =request.form['postcode']
					
                    # Details validation. "check_address" function checks if the input matches the requirements
					address_validation = check_address(house_number,street_name, city, country, postcode)
					if address_validation!= True:
						return render_template('checkout.html',error_address=address_validation)


                    # check if the checkbox for skipping the billing address has been checked
					answer = request.form.get('answer')
                    # if a user wants to make billing address the same as current address, 
                    # make variables for billing address equal to the data user entered in current address fields
					if ((answer != None) or ('enter_billing_address' not in session)):
							bill_house_number = house_number
							bill_street_name = street_name
							bill_city = city
							bill_country = country
							bill_postcode = postcode 
							if 'enter_billing_address' in session:
								session.pop(	'enter_billing_address', None)
							session.modified = True
											# if no, tak the biling address data from the form 
					else:                        
							bill_house_number = request.form['bill_house_number']
							bill_street_name = request.form['bill_street_name']
							bill_city = request.form['bill_city']
							bill_country = request.form['bill_country']
							bill_postcode =request.form['bill_postcode']

								# Due to the autofill function of billing address, I cannot use "required" attribute for billing address fields in html, 
								# so I put all the variables in a list and check if they are not None (empty string). 
							array = [bill_house_number, bill_street_name, bill_city, bill_country, bill_postcode]
							for data in array:
								if data == '':
									# if some field was not filled in, I return the user to the same page and show an error
									return render_template('checkout.html',error_billing_address="Enter billing address")

							# Billing address validation. "check_address" function checks if theinput matches the requirements
							billing_address_validation = check_address(bill_house_number,bill_street_name, bill_cit, bill_country, bill_postcode)
							if billing_address_validation!= True:
								return render_template('checkout.html',error_billing_address=billing_address_validation)
                   
                    # take card details data from the form
					card_number = request.form['card_number']
					name_on_card = request.form['name_on_card']
					expiry_date = request.form['expiry_date']
					card_cvv =request.form['cvv']
                    
          # Card details validation. "check_address" function checks if the input matches the requirements

					card_validation = check_card(card_number,name_on_card, expiry_date, card_cvv)
					if card_validation!= True:
						 return render_template('checkout.html',error_card=card_validation)


                    # generate random transaction number using python random module
                    # and make sure this new generated number does not already exist in the table

					transaction_number = (random.randint(0,999999999))
					con.execute('SELECT transaction_number FROM orders;')
					transaction_number_array = cur.fetchall()
					while transaction_number in transaction_number_array:
						transaction_number = (random.randint(0,999999999)) 
                    
                    # take total price value from the session
					all_total_price = session['all_total_price']
 
                    # insert all the data to the orders table. Order ID will be automatically generated
					con.execute("INSERT INTO orders(order_email, order_firstname, order_lastname, transaction_number, total_price, card_number , card_name , card_date, card_cvv ) VALUES (?,?,?,?,?,?,?,?,?)", ( user_email, firstname, lastname, transaction_number, all_total_price, card_number, name_on_card, expiry_date, card_cvv ))
					# Since the transaction number is unique for each order and cannot be repeated, using it, 
					# I take the id for this new order that was just generated in the orders table.
					cur.execute("SELECT order_id FROM orders WHERE transaction_number=?;", (transaction_number,))
					row = cur.fetchone()
					_order_id = row[0]

                    # insert address data to the order_address table using order ID as a primary key
					con.execute("INSERT INTO order_address(order_id, house_number, bill_house_number, street_name, bill_street_name, city, bill_city, country, bill_country, postcode, bill_postcode) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (_order_id,house_number, bill_house_number, street_name, bill_street_name, city, bill_city, country, bill_country, postcode, bill_postcode))

                    # using loop add each item from users cart to the order_items table (here I also use the order ID as a PK)
					for key, val in session['cart_item'].items():
							item_code = session['cart_item'][key]['code']
							quantity = int(session['cart_item'][key]['quantity'])
							con.execute("INSERT INTO order_items(order_id, item_code, quantity) VALUES(?, ?, ?)", (_order_id,item_code, quantity))
					
					con.commit()
					cur.close()
					con.close()
					
                    
					return show_order_info(_order_id)
		except Exception as e:
			print(e)

# Function for displaying order confirmation. It is used on order_done page. 
# it takes one parameter - order id
def show_order_info(order_id):
    try:
        con = sqlite3.connect('products.db')
        cur = con.cursor()
				# connects to the database and takes data for the order using its ID. Data is taken from two tables. 
        cur.execute("SELECT * FROM order_address INNER JOIN orders ON order_address.order_id = orders.order_id WHERE orders.order_id=?;", (order_id,))
        order_data = cur.fetchone()

        # takes codes for ordered items from the "order_items" table (using order ID)
        cur.execute("SELECT item_code FROM order_items WHERE order_id=?;", (order_id,))
        order_items_code = cur.fetchall()

        # create a new list for all the order's data
        data = []
        # add first part to the list
        data.append(order_data)

        x=0
        items = []
        while x!=len(order_items_code):
						# using the list of codes of the ordered items, go to the table "products" and take data (name) about each product ordered
            cur.execute("SELECT name FROM products WHERE code=?;", (order_items_code[x][0],))
            row = cur.fetchone()
            # convert list with one item to string 
            r = ' '.join(row)
            # add string to the "data" list
            items.append(r)
            #data.append(r)
            x=x+1

        cur.close()
        con.close()
       # when order is done, remove items from cart and close it if it was opened
        session.pop('open_cart', None)
        session.pop('cart_item', None)
        session.pop('buy_now_register', None)
        session.modified = True

        return render_template('order_done.html', data=data, items=items )
    except Exception as e:
        print(e)


# Function for "buy now" and "add to cart" buttons from the home page. 
# It distinguishes what exactly the user wants to do 
# with the selected product - buy it right away or put it in the cart
@app.route('/add', methods=['POST'])
def add():
    
	# takes items code and quantity from the form 
    _quantity = int(request.form['quantity'])
    _code = request.form['code']
		# checks if form was posted successfully and variables are not None
    if _quantity and _code and request.method == 'POST':
        # checks if requested quantity of items is not greater than current in stock value
        con = sqlite3.connect('products.db')
        cur = con.cursor();
        # take current in_stock value
        cur.execute("SELECT in_stock FROM products WHERE code=?;", [_code])
        row = cur.fetchall()
        current_in_stock = row[0][0]
        # this if statement will not allow user to add items to cart if requested quantity is greater than current in stock quantity
        if current_in_stock < _quantity:
            return redirect(url_for('.products'))

			# takes the action value from the form. This is the name of the pressed button. 
        _action = request.form['action']
				# if user want to buy item now, function puts item in the cart and redirects user to the buy now page
        if _action == "Buy Now":
            add_to_cart(_quantity, _code)
            if 'user' in session:
                return redirect(url_for('.checkout'))
            else:
                session['buy_now_register'] = 'yes'
                return render_template('buy_now.html')
        else:
						# else just puts item in the cart
            return add_to_cart(_quantity, _code)
    else:
        return 'Error while adding item to cart'


# Function that puts items to cart and creates array with items in the cart
# takes item code and quantity
# Some of the functions (add_to_cart, delete_product, array_merge) were adapted from "shopping cart" tutorial ( 5009CEM, 9n the week 5 lab) 
# Reference: https://coventry.aula.education/?#/dashboard/5f5fd4db-69fa-4d4e-ad94-7a7f6084c1e9/journey/materials/b3f127ff-5c46-45ee-8776-acef862451b7 
def add_to_cart(quantity, code):
    cursor = None
    try:
	
        con = sqlite3.connect('products.db')
        cur = con.cursor();
				# takes selected items name, image, price (format it to 2 decimal places) etc from "products" table using its id
        cur.execute("SELECT * FROM products WHERE code=?;", [code])
        row = cur.fetchone()
        new_in_stock = row[5]-quantity
        cur.execute("UPDATE products SET in_stock=? WHERE code=?", (new_in_stock,code))

				# put the data to "itemArray" array
        itemArray = { row[2] : {'name' : row[1], 'code' : row[2], 'quantity' : quantity, 'price' : row[4], 'image' : row[3], 'total_price': quantity * row[4]}}
                    
        all_total_price = 0
        all_total_quantity = 0
                    
        session.modified = True
        # if cart is not empty, 
        if 'cart_item' in session:
					# if the cart already contains the selected product, update the quantity
            if row[2] in session['cart_item']:
                for key, value in session['cart_item'].items():
                    if row[2] == key:
                        old_quantity = session['cart_item'][key]['quantity']
                        total_quantity = old_quantity + quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        session['cart_item'][key]['total_price'] = total_quantity * row[4]
											
						# if there is no selected item in the cart
						# add created array to the existing one in the session
            else:
                session['cart_item'] = array_merge(session['cart_item'], itemArray)

          #  add the price and quantity of an item to the total price and quantity of items in the cart          
            for key, value in session['cart_item'].items():
                individual_quantity = int(session['cart_item'][key]['quantity'])
                individual_price = float(session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price
					# if cart is empty, add created array to the session 
        else:
            session['cart_item'] = itemArray
						# add item price and quatity to all_total_quantity and all_total_price variables
            all_total_quantity = all_total_quantity + quantity
            all_total_price = all_total_price + quantity * row[4]
        
        
				# update all_total_price and all_total_quantity variables in the session   
        

        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
        session.modified = True

        # redirect user to the homepage
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)
    finally:
        con.commit()
        cur.close()
        con.close()
                


# Function for the homepage, it displays all the products from the database
@app.route('/')
def products():
    try:
        con = sqlite3.connect('products.db')
        cur = con.cursor();
        # select all columns fom the product table, format price column to display it with 2 decimal places, do not select items that are out of stock
        cur.execute("SELECT id, name,code, image, printf('%.2f',price) , in_stock, manufacturer, category FROM products WHERE in_stock >=1")
        rows = cur.fetchall()
        return render_template('home.html', products=rows)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        con.close()

# Login function. 
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # if before pressing "login" button user didn't clos the cart, remove this value from session
        if 'open_cart' in session:
            session.pop('open_cart', None)
			# if before pressing "login" button user tried to check out as a guest, remove this value from session
        if 'checkout_as_guest' in session:
            session.pop('checkout_as_guest', None)
			# check if form was posted and take email and password from ir 
        if request.method == 'POST':
            email = request.form['email']
            password =request.form['password']
            con = sqlite3.connect('products.db')
            cur = con.cursor()

            # search for entered email and password in the database
						# if the user was found, add his/her email to the session  
            cur.execute("SELECT count(*) FROM users WHERE email=? AND password=?;", (email, password))
            if int(cur.fetchone()[0]) > 0:
                session['user'] = email
                session.modified = True
                print("logged in IN as: ", email)
                if 'buy_now_register' in session:
                    return redirect(url_for('.checkout'))
                return redirect(url_for('.products'))
						# if email and password weren't found, check if user entered wrong password. 
						# Search only for the entered email in te database
            else:
                cur.execute("SELECT count(*) FROM users WHERE email=?;", (email, ))
                row = cur.fetchone()
								# if entered email wasn't found, redirect user back to the login page and show error "wrong details"
                if row[0] == 0 :
                    error_msg = "Email is incorrect!"
                    return render_template('login.html',error_msg=error_msg)
								# if entered email was found, redirect user back to the login page and show error "wrong password"
                else:
                    error_msg = "Password is incorrect!"
                    return render_template('login.html',error_msg=error_msg)
    
        error_msg = None
        return render_template('login.html',error_msg=error_msg)
        
    except Exception as e:
        print(e)


# Logout function. Removedsusers data from the session and redirect to the homepage
@app.route('/logout')
def logout():
    try:
        session.pop('user', None)
        session.pop('open_cart', None)
        session.pop('cart_item', None)
        session.pop('buy_now_register', None)
        session.modified = True
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        # if before pressing "login" button user didn't clos the cart, remove this value from session
        if 'open_cart' in session:
            session.pop('open_cart', None)
			 # if user that wants to register is already logged in to another account, log him out
        if 'user' in session:
            session.pop('user', None)
            session.modified = True
				
				# make sure the form was posted successfully and take the data from it
        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            password =request.form['password']
            
            # firstname, lastname, email and password validation, if function returned True, it means an input matches the criteria
			# if something else was returned, users is redirected back to refill the form, and also error message is shown
            details_validation = register_data_validation(firstname,lastname, email, password )
            if details_validation != True:
                return details_validation
            else:
                # add entered data to the database table "users" and redirect user to the login page
                con = sqlite3.connect('products.db')
                cur = con.cursor()
                con.execute("INSERT INTO users(firstname, lastname, email, password) VALUES(?, ?, ?, ?)", (firstname, lastname, email, password))
                con.commit()
                cur.close()
                con.close()
                return redirect(url_for('.login'))

        # remove text message from error_msg variable
        error_msg = None
        return render_template('register.html',error_msg=error_msg)
    except Exception as e:
        print(e)


# This function is used on buy_now page, when users pressed "buy now" button 
# and chose not to register to buy an item
@app.route('/checkout_as_guest')
def checkout_as_guest():
    try:
        	# if user clicks on "register" and then decides to go back continue as a guest, remove 'buy_now_register' from session
        if 'buy_now_register' in session:
            session.pop('buy_now_register', None)
			# this function adds information that user wants to checkout as a guest to the session
        session['checkout_as_guest'] = "guest"
			#  sets 'enter_billing_address' as not None. 
        session['enter_billing_address'] = "yes"
        session.modified = True
			# redirects user to the checkout page to enter address and card details
        return render_template('checkout.html')
    except Exception as e:
        print(e)


# This function is used on homepage page, when users pressed "checkout" button on the cart
@app.route('/checkout')
def checkout():
    try:
			# closes the cart if it is opened
        if 'open_cart' in session:
            session.pop('open_cart', None)

						# adds information that user wants to checkout as a guest to the session
            if 'user' not in session:
                session['checkout_as_guest'] = "guest"
          
						# adds information that user didn't click checkbox to skip billing address form yet
            session['enter_billing_address'] = "yes"
            session.modified = True

				# redirects user to the checkout page to enter address and card details 
        return render_template('checkout.html')
    except Exception as e:
        print(e)

# This function is used in navigation bar, 
# it gets category name ("word") from html file
@app.route('/search/<string:word>')
def search(word):
    try:
        # puts the name of the selected category in the session so that it can be displayed on the html page
        session['search'] = str(word)
				# updates the session
        session.modified = True
			  # connects to the database
        con = sqlite3.connect('products.db')
				# creates the cursor
        cur = con.cursor();
				# executes a query to select all items with a specific category
        if (word == "laptop" or word == "phone" or word == "tablet"):
            cur.execute("SELECT * FROM products WHERE category =?;", [word])
        rows = cur.fetchall()
				# removes error message that can be left from previous searches
        if 'nothing_to_show' in session:
            session.pop('nothing_to_show', None)
            # passes the result to the html page
        return render_template('search.html', products=rows)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        con.close()


# This function is used in search bar, 
# it gets input from the form

@app.route('/search_str', methods=['POST'])
def search_str():
    try:
        # removes error message that can be left from previous searches
        if 'nothing_to_show' in session:
            session.pop('nothing_to_show', None)
				# takes input from the form
        string = request.form['string']
				# puts it in the session so that it can be displayed on the html page
        session['search'] = str(string)
				# updates the session
        session.modified = True
				# connects to the database
        con = sqlite3.connect('products.db')
				# creates the cursor
        cur = con.cursor();
				# Adds percent signs at the beginning and end of an input so that it can be inserted into a query
        name_or_manufacturer = ('%'+string+'%')
				 # Searches for matches with the item name or item manufacturer 
        cur.execute("SELECT * FROM products WHERE (name LIKE ? or manufacturer LIKE ?)", (name_or_manufacturer,name_or_manufacturer,))
        rows = cur.fetchall()
        print("rows:"+str(rows))
				# If there are no results, it shows the search results page and passes the message in session 
        if not rows:
            session['nothing_to_show'] = 'nothing_to_show'
            session.modified = True
				#  otherwise, the search results are displayed one the search page
        cur.close()
        con.close()
        return render_template('search.html', products=rows)
    except Exception as e:
        print(e)

        
# Fucntion to remove items from cart
@app.route('/empty')
def empty_cart():
    try:
			# removes cart_items from sesssion
        session.pop('cart_item', None)
        session.pop('open_cart', None)
        session.modified = True
			# redirects to the homepage
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)

# Function (and route) to open and close the cart.
@app.route('/open_cart')
def open_cart():
    try:
			# if it is opened, close it by removing "open_cart" from session 
        if 'open_cart' in session:
            session.pop('open_cart', None)
			# else open it by adding "open_cart" to the session 
        else:
            session['open_cart'] = "open"
				# update session 
        session.modified = True
				# redirect to the same page
        return redirect(request.referrer)
    except Exception as e:
        print(e)


# Function to remove item from cart
@app.route('/delete/<string:code>/<string:quantity>')
def delete_product(code,quantity):
	try:
		all_total_price = 0
		all_total_quantity = 0
		session.modified = True

		# iterate through all the items in the cart and find the one we need by id
		for item in session['cart_item'].items():
			if item[0] == code:
				# remove it from the cart 						
				session['cart_item'].pop(item[0], None) 
				# update the price and quantity values.
				if 'cart_item' in session:
					for key, value in session['cart_item'].items():
						individual_quantity = int(session['cart_item'][key]['quantity'])
						individual_price = float(session['cart_item'][key]['total_price'])
						all_total_quantity = all_total_quantity + individual_quantity
						all_total_price = all_total_price + individual_price
				break

		# if it was the last item in the cart, 
		# remove cart_items from the session (to show the user message that cart is empty)
		# and close the bag
		if all_total_quantity == 0:
			session.pop('open_cart', None)
		    # if it wasn't update all_total_price and all_total_quantity variables in session

		else:
			session['all_total_quantity'] = all_total_quantity
			session['all_total_price'] = all_total_price
		# update the session
		session.modified = True
		
        # update removed product instock quantity by adding removed quantity back to the table
		con = sqlite3.connect('products.db')
		cur = con.cursor();
        # take current in stock value
		cur.execute("SELECT in_stock FROM products WHERE code=?;", [code])
		row = cur.fetchall()
		old_in_stock = row[0][0]
        # create new variable for new stock value and add removed from cart quantity to the old stock value
		new_in_stock = int(old_in_stock)+int(quantity)
        # update "in_stock" column in the products table 
		cur.execute("UPDATE products SET in_stock=? WHERE code=?", (new_in_stock,code))
		con.commit()
		cur.close()
		con.close()
		return redirect(url_for('.products'))
	except Exception as e:
		print(e)
		

# This function merges two arrays/dictionaries/sets. It is used for adding item in the cart

def array_merge( first_array , second_array ):
	if isinstance( first_array , list ) and isinstance( second_array , list ):
		return first_array + second_array
	elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
		return dict( list( first_array.items() ) + list( second_array.items() ) )
	elif isinstance( first_array , set ) and isinstance( second_array , set ):
		return first_array.union( second_array )
	return False		



def check_address(house_number, street_name, city, country, postcode):
    array = [house_number, street_name, city, country, postcode]
    for item in array:
        if(re.search('[@$!%*#?&]',item) is not None):
            return "Address cannot contain special characters."
    if (len(postcode) > 8):
        return "Postcode is too long."
    else:
        return True



# Function for firstname, lastname and email validation in checkout form. 
# It uses already exsisting function that are also used for register form

def payNow_data_validation(firstname,lastname, email):
    firstname_lastname_valid = check_firstname_lastname(firstname, lastname)
    if firstname_lastname_valid != True:
        return render_template('checkout.html',error_name_email=firstname_lastname_valid)
    email_valid = check_email(email)
    if email_valid != True:
        return render_template('checkout.html',error_name_email=email_valid)
    else:
        error_name_email = None
        return True



# Function for regitration from data validation. 
# it uses already exsisting function that are also used for checkout form

def register_data_validation(firstname,lastname, email, password ):
    print("register_data_validation")
    # firstname and lastname validation, 
    firstname_lastname_valid = check_firstname_lastname(firstname, lastname)
    if firstname_lastname_valid != True:
        return render_template('register.html',error_msg=firstname_lastname_valid)
    print("firstname_lastname_valid")
    # email validation, 
    email_valid = check_email(email)
    if email_valid != True:
        return render_template('register.html',error_msg=email_valid)
    print("email_valid")
    # password validation, 
    password_valid = check_password(password)
    if password_valid != True:
        return render_template('register.html',error_msg=password_valid)
    else:
        return True

# Function for firstname and lastname validation. It checks if entered firstname and lastname does not:
# 1. contain numbers 
# 2. contain special characters

def check_firstname_lastname(firstname, lastname):
    if ((re.search('[0-9]',firstname) is not None) or (re.search('[0-9]',lastname) is not None)):
        error_msg= "Your name can contain only letters. "
        return error_msg
    elif ((re.search('[@$!%*#?&]',firstname) is not None) or (re.search('[@$!%*#?&]',lastname) is not None)):
        error_msg= "Your name cannot contain special characters. "
        return error_msg
    else:
        # if firstname and lastname matches the criteria, return TRUE
        error_msg = None
        return True


# Function for email validation. It checks if entered email is in the right format:  username@company.domain 
# reference: https://www.tutorialspoint.com/python-program-to-validate-email-address
# it also check if entered email is already in the database


def check_email(email):
    example = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    con = sqlite3.connect('products.db')
    cur = con.cursor();
    cur.execute("SELECT count(*) FROM users WHERE email=?;", (email, ))
    row = cur.fetchone()
    if row[0] != 0:
        print(str(row))
        error_msg= "Email already exists "
        return error_msg
    elif re.match(example,email):
        error_msg = None
        return True
    else:
        error_msg= "Please enter an existing email. "
        return error_msg



# Function for password validation. It checks if entered password:
# 1.is too long/short 
# 2. contains at least one number 
# 3. contains upcase and one lowcase letter

def check_password(password):
    if (len(password) < 10 or len(password) > 20):
        error_msg= "Make sure your password length is min 10 max 20 characters. "
        return error_msg
    elif re.search('[0-9]',password) is None:
        error_msg= "Make sure your password has a number in it. "
        return error_msg
    elif ((re.search('[A-Z]',password) is None) or (re.search('[a-z]',password) is None)): 
        error_msg= "Make sure your password has one upcase and one lowcase letter. "
        return error_msg
    else:
			# if the password matches the criteria, return TRUE
        return True




# card validation. 
# To make this website testable for me and lecturers and also to avoid storing real card numbers, 
# card info is not checked properly. Function only checks it's length, that card number starts with a 4,5 or 6 
# and that it only consist of digits (0-9).  
#https://codereview.stackexchange.com/questions/169530/validating-credit-card-numbers

def check_card(card_number, name, date, cvv):
    error_card = None

# check card_number
    if card_number.isnumeric() != True:
        error_card= "Card number is not numeric."
        return error_card
    elif card_number[0] not in ['4','5','6']:
        error_card= "Card number is invalid"
        return error_card
    elif len(card_number) != 16:
        error_card= "Card number is too long/short"
        return error_card

# check name on card
    elif ((re.search('[0-9]',name) is not None) or (re.search('[@$!%*#?&]',name) is not None)):
        error_card= "Name can only contain letters"
        return error_card

# check cvv code
    elif ((len(cvv) != 3) or(cvv.isnumeric() != True)):
        error_card= "CVV is invalid"
        return error_card

# check expiry date
    elif (re.search('[@$!%*#?&]',date) is not None):
        error_card= "Expiry Date cannot contain special characters"
        return error_card
    elif ((re.search('[a-z]',date) is not None) or (re.search('[A-Z]',date) is not None)):
        error_card= "Expiry Date cannot contain letters"
        return error_card
    elif len(date) != 5:
        error_card= "Expiry Date is too short/long"
        return error_card

    else:
      	return True 






if __name__ == "__main__":
    #app.run(port=5000)
    app.run()