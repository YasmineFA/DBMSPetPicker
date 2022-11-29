# from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'CS542Team1'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = #'pfadmin@petfinderdb'
# app.config['MYSQL_PASSWORD'] = 'pfapi2022!'
# app.config['MYSQL_DB'] = 'guest'

mysql = MySQL(app)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['fname']
      pwd = request.form['pwd']
      if request.form['authorize'] == "Login":
         # print(user)
         # print(pwd)
         # check username and pwd are correct
         if(auth_login(user, pwd)):
            return redirect(url_for('account',user = user))
         else:
            flash("Incorrect login, please try again", category='error')
            return redirect(url_for('index'))

      elif request.form['authorize'] == "Register":
         # check username isn't taken
         if(sign_up(user, pwd)):
            flash("Account created", category='success')
            return redirect(url_for('account', user = user))
         else:
            return redirect(url_for('index'))
      else:
         return redirect(url_for('index'))
   else:
      return redirect(url_for('index'))

@app.route("/account/<user>")
def account(user):
   queryList = getSavedSearches(user)
   return render_template('account.html', username=user, searches=queryList)

@app.route("/results/<query>", methods=['POST'])
def results(query):
   return render_template('results.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def connectDB():
   conn = mysql.connector.connect(
         host="localhost",
         user="root",
         password="root",
         database="petfinderDB"
         )
   return conn

def auth_login(user, pwd):
   conn = connectDB()
   cur = conn.cursor()
   cur.execute("SELECT * FROM users WHERE username = % s AND password = % s", (user, pwd))
   account = cur.fetchone()
   if account:
      session['loggedin'] = True
      session['id'] = account['id']
      session['username'] = account['username']
      cur.close()
      conn.close()
      return True
   else:
      cur.close()
      conn.close()
      return False

def sign_up(user, pwd):
   # check password meets requirements
   if(len(pwd) < 8):
      flash("Password is too short", category='error')
      return False
   # check username isn't taken
   conn = connectDB()
   cur = conn.cursor()
   cur.execute("SELECT * FROM user WHERE username = % s AND password = % s", (user, pwd))
   accExists = cur.fetchone()
   if(accExists==None):
      # add account info into users table
      cur.execute("INSERT INTO user WHERE username = % s AND password = % s", (user, pwd))
      conn.commit()
      session['loggedin'] = True
      session['id'] = account['id']
      session['username'] = account['username']
      cur.close()
      conn.close()
      return True
   else:
      flash("Username already taken", category='error')
      cur.close()
      conn.close()
      return False

def getSavedSearches(user):
   conn = connectDB()
   cur = conn.cursor()
   cur.execute("SELECT searchQuery FROM user WHERE username= % s", (user))
   searches = cur.fetchone()
   queryList = searches.split(', ')
   return queryList 

if __name__ == '__main__':
   app.run(debug=True)