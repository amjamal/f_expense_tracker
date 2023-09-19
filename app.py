#pip install flask
#pip install flask-mysqldb - for using mysql
#render_template for passing the html

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

#referencing the file
app = Flask(__name__)

app.secret_key = 'amjexpensetracker1234'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "mysql_databases"
app.config['MYSQL_DB'] = "expense_tracker"

mysql = MySQL(app)

#setting the url using decorator function
@app.route('/')   #homepage

#defining the function for the route
def index():
    msg2=''   #variable need to be assigned outside to avoid error
    if 'loggedin' in session:
        usr = session['username']     #to get the username at the top right corner
        msg2 = "This is the home page, Click Add on the left to add new expenses..."
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        #cursor.execute('SELECT * FROM expenses ORDER BY date DESC LIMIT 5')
        cursor.execute('(SELECT * FROM expenses ORDER BY date DESC LIMIT 5)ORDER BY date ASC')

        expenses = cursor.fetchall()        #fetch all the data from table
        expense_list=[]

        for i in range(len(expenses)):
            expenses[i]['date'] = expenses[i]['date'].strftime('%d-%m-%Y')
            expense_list.append(expenses[i])



        return render_template('home.html', usr=usr, msg2=msg2, expense_list=expense_list) #passing the values to the html page
    return redirect(url_for('login'))

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():  
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']  #this values are required to authenticate the user

#MySQLdb.cursors.DictCursor argument specifies that the cursor should return rows as dictionaries instead of tuples
#import MySQLdb.cursors
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM credentials WHERE username = %s \
                AND password = %s', (username, password))
        credentials = cursor.fetchone()  #fetch the username and password details from credentials table
        if credentials:
            session['loggedin'] = True
            session['username'] = credentials['username']
            session['password'] = credentials['password']   #this validates the username and password

            #msg = f'Hai {credentials["name"]}, You are logged in successfully.'
            return redirect(url_for('index'))
        else:
            msg = 'Invalid username/password!'


    return render_template('login.html', msg=msg)

#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

#add new expense
@app.route('/expense', methods=['POST', 'GET'])
def expense():
    exp=''
    usr=''
    msg=''

    if 'loggedin' in session:
        usr = session['username']
        if request.method == 'POST' and 'billname' in request.form and 'amount' in request.form\
            and 'payment' in request.form and 'category' in request.form and 'billdate' in request.form:
            name = request.form['billname']
            amount = request.form['amount']
            payment = request.form['payment']
            category = request.form['category']
            date = request.form['billdate']   #gets the values from form and assigns to the variables

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO expenses VALUES (%s, %s, %s, %s, %s)', (name, amount, payment, category, date))
            mysql.connection.commit()
            exp = "Your expense is added successfully"
            return render_template('expense.html', exp=exp)  #if expense added successfully the value in 'exp' will be passed
    elif 'loggedin' not in session:
        return redirect(url_for("login"))    #if not logged in it will redirect to login page    
    return render_template('expense.html', exp=exp, usr=usr)    

#List all the expenses 
@app.route('/allexpenses', methods=['POST', 'GET'])
def allexpenses():
    if 'loggedin' in session:
        usr = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        payment_value = request.form.get('payment')  #get the selected payment value from the form
        category_value = request.form.get('category') #get the selected category value from the form

        if (payment_value and category_value):  #if condition for payment and category
            cursor.execute('SELECT * FROM expenses WHERE payment=%s AND category=%s', [payment_value, category_value])

        elif payment_value:   #if condition for payment
            cursor.execute('SELECT * FROM expenses WHERE payment=%s', [payment_value])

        elif category_value:  #if condition for category
            cursor.execute('SELECT * FROM expenses WHERE category = %s', [category_value])

        else:   #if no conditions display all the expenses without filter
            cursor.execute('SELECT * FROM expenses')

        expenses = cursor.fetchall()    #fetch all the datas from table
        expense_list=[]

        for i in range (len(expenses)):
            #convert the date to DD-MM-YYYY format
            expenses[i]['date'] = expenses[i]['date'].strftime('%d-%m-%Y')

            #the result set is in dictionary, so this gets the value from key
            expense_list.append(expenses[i])
            #amounts.append(expenses[i]['amount'])

    elif 'loggedin' not in session:
        return redirect(url_for("login"))
    #the values are passed so that they are displayed when selected
    return render_template('all_expenses.html', payment_value=payment_value, category_value=category_value, usr=usr, expense_list=expense_list)


if __name__ == "__main__":
    app.run(debug=True)

#use "python app.py" to run