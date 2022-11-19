from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import sqlite3 as sql
import re
import alert 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import dotenv_values
app = Flask(__name__)


envData=dotenv_values("./.env")
hostname = '9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud'
uid = 'wnj72009'
pwd = 'SaVB6WawnXIACwio'
driver = "{IBM DB2 ODBC DRIVER}"
db_name = 'bludb'
port = '32459'
protocol = 'TCPIP'
cert = "DigiCertGlobalRootCA.crt"
dsn = (
    "DATABASE ={0};"
    "HOSTNAME ={1};"
    "PORT ={2};"
    "UID ={3};"
    "SECURITY=SSL;"
    "PROTOCOL={4};"
    "PWD ={6};"
).format(db_name, hostname, port, uid, protocol, cert, pwd)
conn = ibm_db.connect(dsn, "", "")
print()

print("Connecting Successful!!!!!!!!")

app.secret_key = 'jackiechan'

@app.route('/')

def homer():
    return render_template('home.html')


@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account['USERNAME']
            userid=  account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'Logged in successfully !'
            return render_template('dashboard.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)


@app.route('/admin_login',methods =['GET', 'POST'])
def admin_login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM adminlogin WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account['USERNAME']
            userid=  account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'Logged in successfully !'
            return redirect(url_for('view2'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('admin_login.html', msg = msg)      

   
@app.route('/register', methods =['GET', 'POST'])
def registet():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO  users VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = 'Please fill out the form !'
        if request.method == 'POST':
          msg = 'You have successfully registered! Please login !'
        #   sendgridmail(email,msg)
    return render_template('register.html', msg = msg) 

@app.route('/add_stock',methods=['GET','POST'])
def add_stock():
    msg=''
    if request.method == "POST":
        prodname=request.form['prodname']
        quantity=request.form['quantity']
        warehouse_location=request.form['warehouse_location'] 
        sql='SELECT * FROM product WHERE prodname =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,prodname)
        ibm_db.execute(stmt)
        acnt=ibm_db.fetch_assoc(stmt)
        print(acnt)
            
        if acnt:
            msg='Product already exits!!'
            return render_template("add_stock.html",msg=msg)    
        else:
            insert_sql='INSERT INTO product VALUES (?,?,?)'
            pstmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(pstmt,1,prodname)
            ibm_db.bind_param(pstmt,2,quantity)
            ibm_db.bind_param(pstmt,3,warehouse_location)
            ibm_db.execute(pstmt)
            msg='You have successfully added the products!!'
            return render_template("dashboard.html")      

    else:
        msg="fill out the form first!"
        return render_template('add_stock.html',meg=msg)

@app.route('/delete_stock',methods=['GET','POST'])
def delete_stock():
    if(request.method=="POST"):
        prodname=request.form['prodname']
        sql2="DELETE FROM product WHERE prodname=?"
        stmt2 = ibm_db.prepare(conn, sql2)    
        ibm_db.bind_param(stmt2,1,prodname)
        ibm_db.execute(stmt2)

        flash("Product Deleted", "success")

        return render_template("dashboard.html")

@app.route('/update_stock',methods=['GET','POST'])
def update_stock():
    mg=''
    if request.method == "POST":
        prodname=request.form['prodname']
        quantity=request.form['quantity']
        quantity=int(quantity)
        print(quantity)
        print(type(quantity))
        warehouse_location=request.form['warehouse_location'] 
        sql='SELECT * FROM product WHERE prodname =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,prodname)
        ibm_db.execute(stmt)
        acnt=ibm_db.fetch_assoc(stmt)
        print(acnt)
            
        if acnt:
            insert_sql='UPDATE product SET  quantity=?,warehouse_location=? WHERE prodname=? '
            pstmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(pstmt,1,quantity)
            ibm_db.bind_param(pstmt,2,warehouse_location)
            ibm_db.bind_param(pstmt,3,prodname)
            ibm_db.execute(pstmt)
            mg='You have successfully updated the products!!'
            limit=5
            print(type(limit))
            if(quantity<=limit):
                   alert("Please update the quantity of the product {}, Atleast {} number of pieces must be added!".format(prodname,10))
            return render_template("dashboard.html",meg=mg)   
            
        else:
             mg='Product not found!!'
               

    else:
         msg="fill out the form first!"
         return render_template('update_stock.html',meg=msg)

@app.route('/view_stock')
def view_stock():
   
    sql = "SELECT * FROM product"
    stmt = ibm_db.prepare(conn, sql)
    result=ibm_db.execute(stmt)
    print(result)

    products=[]
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
    products=tuple(products)
    print(products)

    if result>0:
        return render_template('view.html', products = products)
    else:
        msg='No products found'
        return render_template('view.html', msg=msg)

@app.route('/view2')
def view2():

    sql = "SELECT * FROM product"
    stmt = ibm_db.prepare(conn, sql)
    result=ibm_db.execute(stmt)
    print(result)

    products=[]
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
    products=tuple(products)
    print(products)

    if result>0:
        return render_template('view2.html', products = products)
    else:
        msg='No products found'
        return render_template('admin_login.html', msg=msg)
    

@app.route('/delete')
def delete():
    return render_template('delete_stock.html')

@app.route('/update')
def update():
    return render_template('update_stock.html')
    

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

@app.route("/send")
def send():
	

		query="select email from prodect "
		
		stmt = ibm_db.prepare(conn, query)
		ibm_db.execute(stmt)
		data = ibm_db.fetch_assoc(stmt)
		print(data) 
		message = Mail(from_email='empire44440@gmail.com',to_emails=data['EMAIL'],subject='Sending with Twilio SendGrid is Fun',html_content='<strong>and easy to do anywhere, even with Python</strong>')
		try:
			sg = SendGridAPIClient('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')
			response = sg.send(message)
			print(response.status_code)
			print(response.body)
			print(response.headers)
		except Exception as e:
			print(e)
		return redirect(url_for("view2"))
    
if __name__ == '__main__':
   app.run(host='0.0.0.0')
