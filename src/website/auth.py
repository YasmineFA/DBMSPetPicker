import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# from flaskr.db import get_db

auth = Blueprint('auth', __name__)

@auth.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      if request.form['authorize'] == "Login":
         user = request.form['fname']
         pwd = request.form['pwd']
         # print(user)
         # print(pwd)
         # check username and pwd are correct
         return render_template('account.html') #redirect(url_for('account',name = user))
      elif request.form['authorize'] == "Register":
         user = request.form['fname']
         pwd = request.form['pwd']
         # check username isn't taken
         if(len(pwd) > 8):
            flash("Account created", category='success')
            return render_template('account.html') #return redirect(url_for('account',name = user))
         else:
            flash("Password is too short, must be at least 8 characters", category='error')
            return render_template('index.html') #return redirect(url_for('index'))
      else:
         return render_template('index.html') #return redirect(url_for('index.html'))
   else:
      return render_template('index.html') #return redirect(url_for('index'))

# @auth.route('/signup',methods = ['POST', 'GET'])
# def signup():
#    if request.method == 'POST':
#       user = request.form['fname']
#       pwd = request.form['pwd']
#       # check username isn't taken
#       if(pwd.length > 8):
#          flash("Account created", category='success')
#          return redirect(url_for('account',name = user))
#       else:
#          flash("Password is too short, must be at least 8 characters", category='error')
#          return redirect(url_for('index'))
#    else:
#       return render_template('index.html') #redirect(url_for('index'))

@auth.route('/logout')
def logout():
    return redirect(url_for('index'))