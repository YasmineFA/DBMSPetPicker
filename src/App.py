from website import create_app
from flask import Flask, render_template, redirect, url_for, request, flash
app = create_app()

# @app.route('/')
# def index():
#    return render_template('index.html')

# @app.route('/login',methods = ['POST', 'GET'])
# def login():
#    if request.method == 'POST':
#       user = request.form['fname']
#       pwd = request.form['pwd']
#       # check username and pwd are correct
#       return redirect(url_for('account',name = user))
#    else:
#       return redirect(url_for('index'))

# @app.route('/signup',methods = ['POST', 'GET'])
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
#       return redirect(url_for('index'))

# @app.route("/account/<user>")
# def account(user):
#    pass

if __name__ == '__main__':
   app.run(debug=True)