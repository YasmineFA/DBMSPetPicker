# from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
import re

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'CS542Team1'
app.config['MYSQL_USER'] = 'pfuser'
app.config['MYSQL_PASSWORD'] = 'pfapi2022!'
app.config['MYSQL_DB'] = 'petfinderdb'
app.config['MYSQL_HOST'] = '34.68.9.43'

# host: 34.68.9.43

# TODO: my local connection, will need to be changed
# app.config['SECRET_KEY'] = 'CS542Team1'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'yfaoua'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'petfinderDB'

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

@app.route("/results", methods=['POST'])
def results():
   # TODO: finish writing this
   # TODO: (Chris) need to finish changes to html
   if request.method == 'POST':
      if(request.form['searchbar'] == None or request.form['searchbar'] == "pet name"):
         flash("nothing to search (please enter a non-default search query)", category='error')
         return redirect(url_for('search'))
      
      petName = request.form['searchbar']
      state = request.form.get('location-select')
      species = request.form.get('species-select')
      age = request.form.get('age-select')
      gender = request.form.get('gender-select')
      size = request.form.get('size-select')
      environment = request.form.get('environment-select')
      attributes = request.form.get('attributes-select')
      results = searchResults(petName, state, species, age, gender, size, environment, attributes)

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
   accounts = cur.fetchone()
   if accounts:
      session['loggedin'] = True
      session['username'] = accounts[0] # first element in tuple is username
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
      session['username'] = user
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
   cur.close()
   return queryList 

def searchOptions(table, column):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT {0} FROM {1};".format(column, table))
   result = cur.fetchall() 
   #get rid of duplicates 
   
   resultList = []
   for entry in result:
      opt = ''.join(map(str, entry))
      if opt not in resultList:
         resultList.append(opt)
   cur.close()
   return sorted(resultList)

def getColNames(table):
   # conn = connectDB()
   conn = mysql.connection
   cur = conn.cursor()
   query = "SELECT CONCAT('\\'', GROUP_CONCAT(column_name ORDER BY ordinal_position SEPARATOR '\\', \\''),'\\'') AS columns FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '" + table + "';"
   # print(query)
   cur.execute(query)
   cols = cur.fetchone()
   colList = cols[0].split(', ')[1:]
   cur.close()
   return colList

def searchResults(petName, state, species, age, gender, size, environment, attributes):
   
   pass
   

if __name__ == '__main__':
   app.run(debug=True)