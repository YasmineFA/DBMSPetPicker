# from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'CS542Team1'
app.config['MYSQL_USER'] = 'pfuser'
app.config['MYSQL_PASSWORD'] = 'pfapi2022!'
app.config['MYSQL_DB'] = 'petfinderdb'
app.config['MYSQL_HOST'] = '34.68.9.43'

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
         # check username and pwd are correct
         if(auth_login(user, pwd)):
            return redirect(url_for('account',user = user))
         else:
            flash("Incorrect login, please try again", category='error')
            return redirect(url_for('index'))

      elif request.form['authorize'] == "Register":
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
   if request.method == 'POST':
      if(request.form['searchbar'] == None or request.form['searchbar'] == "pet name"):
         flash("nothing to search (please enter a non-default search query)", category='error')
         return redirect(url_for('search'))
      
      petName = request.form['searchbar']
      state = request.form.getlist('location-select')
      species = request.form.getlist('species-select')
      age = request.form.getlist('age-select')
      gender = request.form.getlist('gender-select')
      size = request.form.getlist('size-select')
      environment = request.form.getlist('environment-select')
      attributes = request.form.getlist('attributes-select')
      results = searchResults(petName, state, species, age, gender, size, environment, attributes)
      if(request.form.get('save') == "save" and len(results) > 0):
         params = (petName, state, species, age, gender, size, environment, attributes)
         saveQuery(params)
   return render_template('results.html', results=results, user=session['username'])

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
         return render_template('search.html', locations=state, species=species, ages=age, genders=gender, sizes=size, environments=env, user=session['username'])

   else:

      return render_template('search.html', locations=state, species=species, ages=age, genders=gender, sizes=size, environments=env, user=session['username'])

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def auth_login(user, pwd):
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
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute("SELECT searchQuery FROM user WHERE username = '{0}';".format(user))
   searches = cur.fetchone() # TODO: once we have queries, check if we need fetchall
   queryList = list(searches)
   cur.close()
   return queryList 

def searchOptions(table, column):
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
   conn = mysql.connection
   cur = conn.cursor()
   query = "SELECT CONCAT('\\'', GROUP_CONCAT(column_name ORDER BY ordinal_position SEPARATOR '\\', \\''),'\\'') AS columns FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '" + table + "';"
   cur.execute(query)
   cols = cur.fetchone()
   colList = cols[0].replace('\'','').split(', ')[1:]
   cur.close()
   
   return colList

def searchResults(petName, state, species, age, gender, size, environment, attributes):
   query = "SELECT name, link from pets, environment, attributes, petLinks, petStates WHERE pets.id = environment.id AND pets.id = attributes.id AND petLinks.id = pets.id AND petStates.id = pets.id"
   if petName != None and len(petName) > 0 and petName[0] != "":
      query += " AND pets.name like \'" + petName + "\'"
   if state != None and len(state) > 0 and state[0] != "":
      if len(state) == 1:
         query += " AND petStates.state like \'" + state[0] + "\'"
      else:
         query += " AND (petStates.state like \'" + state[0] + "\'"
         for s in state[1,]:
            query += " OR petStates.state like \'" + s + "\'"
         query += ")"
   if species != None and len(species) > 0 and species[0] != "":
      if len(species) == 1:
         query += " AND attributes.species like \'" + species[0] + "\'"
      else:
         query += " AND (attributes.species like \'" + species[0] + "\'"
         for s in species[1,]:
            query += " OR attributes.species like \'" + s + "\'"
         query += ")"
   if age != None and len(age) > 0 and age[0] != "":
      if len(age) == 1:
         query += " AND attributes.age like \'" + age[0] + "\'"
      else:
         query += " AND (attributes.age like \'" + age[0] + "\'"
         for a in age[1,]:
            query += " OR attributes.age like \'" + a + "\'"
         query += ")"
   if gender != None and len(gender) > 0 and gender[0] != "":
      if len(gender) == 1:
         query += " AND attributes.gender like \'" + gender[0] + "\'"
      else:
         query += " AND (attributes.gender like \'" + gender[0] + "\'"
         for g in gender[1,]:
            query += " OR attributes.gender like \'" + g + "\'"
         query += ")"
   if size != None and len(size) > 0 and size[0] != "":
      if len(size) == 1:
         query += " AND attributes.size like \'" + size[0] + "\'"
      else:
         query += " AND (attributes.size like \'" + size[0] + "\'"
         for s in size[1,]:
            query += " OR attributes.size like \'" + s + "\'"
         query += ")"

   if environment != None and len(environment) > 0 and environment[0] != "":
      for e in environment:
         query += " AND environment." + e + " = True"

   if attributes != None and len(attributes) > 0 and attributes[0] != "":
      for a in attributes:
         aNew = a.replace(" ","_").replace("/","_")
         query += " AND attributes." + aNew + " = True"
   query += ";"
   conn = mysql.connection
   cur = conn.cursor()
   cur.execute(query)
   results = cur.fetchall()
   cur.close()

   return results

def saveQuery(query):
   # save query into users table
   try:
      conn = mysql.connection
      cur = conn.cursor()
      savedParams = ""
      first = True
      for item in query:
         if(item != None and len(item) > 0 and item[0] != ""):
            if(not first):
               savedParams += ","
            if(type(item) is str):
               savedParams += item
            else:
               for i in item:
                  savedParams += i
            first = False
      savedParams += ";"
      cur.execute("SELECT searchQuery FROM user WHERE username = '{0}'".format(session['username']))
      prevSaved = cur.fetchone()
      prevSaved = ''.join(map(str, prevSaved))
      q = "UPDATE user SET searchQuery = '{0}' WHERE username = '{1}';".format(prevSaved + savedParams, session['username'])
      print(q)
      cur.execute(q)
      conn.commit()
      cur.close()
      return True
   except:
      flash("failed to save query", category="error")
      return False

if __name__ == '__main__':
   app.run(debug=True)