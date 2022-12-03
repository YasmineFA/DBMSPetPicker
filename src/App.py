# from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')
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

@app.route('/search', methods = ['POST', 'GET'])
def search():
   state = searchOptions("orgs", "state")
   species = searchOptions("attributes", "species") # not in our ER diagram (what was diff between species and breed again?)
   age = searchOptions("attributes", "age")
   gender = searchOptions("attributes", "gender")
   size = searchOptions("attributes", "size")
   env = getColNames("environment")

   if request.method == 'POST':
      # dont use default value of search
      search = request.form["searchbar"]
      if(search == "pet name" or search == ""):
         flash("Please enter a search query", category="error")
         return render_template('search.html', locations=state, species=species, ages=age, genders=gender, sizes=size, environments=env)
      
      # create a sql statement with all the things selected
      # get values of selections
      # state, species, age, gender, size, attributes select where those cols = value
      # env select where col = True

   else:

      return render_template('search.html', locations=state, species=species, ages=age, genders=gender, sizes=size, environments=env)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def connectDB():
   # this is just my local connection for mysql workbench atm
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
   searches = cur.fetchall()
   queryList = searches.split(', ')
   return queryList 

def searchOptions(table, column):
   conn = connectDB()
   cur = conn.cursor()
   cur.execute("SELECT % s FROM % s", (column, table))
   result = cur.fetchall() 
   #get rid of duplicates 
   resultList = []
   for entry in result:
      if entry not in resultList:
         resultList.append(entry)
   return resultList

def getColNames(table):
   conn = connectDB()
   cur = conn.cursor()
   cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = % s;", (table))
   cols = cur.fetchall()
   colList = cols.split(', ')
   return colList
   

if __name__ == '__main__':
   app.run(debug=True)