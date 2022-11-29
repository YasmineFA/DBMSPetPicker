# from flask import Flask
# # from flask_mysqldb import MySQL
# import mysql.connector

# config = {
#     # 'host':'petfinderdb.mysql.database.azure.com',
#     'host' : 'localhost',
#     'user':'pfadmin@petfinderdb',
#     'password':'pfapi2022!',
#     'database':'guest',
#     'client_flags': [mysql.connector.ClientFlag.SSL],
#     'ssl_ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'
# }
# db = mysql.connector.connect(**config)

# # mysql = MySQL(app)



# # try:
# #     conn = mysql.connector.connect(config)
# #     print("Connection established")
# # except mysql.connector.Error as err:
# #     print(err)
# # else:
# #     cursor = conn.cursor()

# def create_app():
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = 'CS542Team1'

#     from .views import views
#     from .auth import auth

#     app.register_blueprint(views, url_prefix="/")
#     app.register_blueprint(auth, url_prefix="/")
#     return app