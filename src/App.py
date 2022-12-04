# from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')
#app.config['SECRET_KEY'] = 'CS542Team1'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = #'pfadmin@petfinderdb'
# app.config['MYSQL_PASSWORD'] = 'pfapi2022!'
# app.config['MYSQL_DB'] = 'guest'

# TODO: my local connection, will need to be changed
app.config['SECRET_KEY'] = 'CS542Team1'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yfaoua'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'petfinderDB'

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
            # TODO: (Chris) figure out how to make the exit button clickable on the flash message
            # should be able to just do it in one place and have it work for them all
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
   # TODO: finish writing this
   # TODO: (Chris) need to finish changes to html
   return render_template('results.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():
   # TODO: add flash message to html file so they actually display
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
    session.pop('username', None)
    return redirect(url_for('index'))

# def connectDB():
#    # this is just my local connection for mysql workbench atm
#    # conn = mysql.connect(
#    #       host="localhost",
#    #       user="yfaoua",
#    #       password="root",
#    #       database="petfinderDB"
#    #       )
#    conn = mysql.connection
#    return conn

def auth_login(user, pwd):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT * FROM user WHERE username = % s AND pwd = % s;", (user, pwd))
   account = cur.fetchone()
   print(account)
   if account:
      session['loggedin'] = True
      session['username'] = account[0] # first element in tuple is username
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
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT * FROM user WHERE username = % s AND pwd = % s;", (user, pwd))
   accExists = cur.fetchone()
   if(accExists==None):
      # add account info into users table
      cur.execute("INSERT INTO user (username, pwd) VALUES (% s, % s);", (user, pwd))
      conn.commit()
      session['loggedin'] = True
      session['username'] = account[0] # first element in tuple is username
      cur.close()
      conn.close()
      return True
   else:
      flash("Username already taken", category='error')
      cur.close()
      conn.close()
      return False

def getSavedSearches(user):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT searchQuery FROM user WHERE username = '{0}';".format(user))
   searches = cur.fetchone() # TODO: once we have queries, check if we need fetchall
   queryList = list(searches)
   return queryList 

def searchOptions(table, column):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT % s FROM % s;", (column, table))
   result = cur.fetchall() 
   #get rid of duplicates 
   resultList = []
   for entry in result:
      if entry not in resultList:
         resultList.append(entry)
   return resultList

def getColNames(table):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = % s;", (table))
   cols = cur.fetchall()
   colList = cols.split(', ')
   return colList
   

if __name__ == '__main__':
   app.run(debug=True)