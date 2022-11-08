from flask import Flask
import mysql.connector
from mysql.connector import errorcode

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'CS542Team1'

    config = {
    'host':'petfinderdb.mysql.database.azure.com',
    'user':'pfadmin>@petfinderdb',
    'password':'pfapi2022!',
    'database':'guest',
    'client_flags': [mysql.connector.ClientFlag.SSL],
    'ssl_ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'
    }

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor = conn.cursor()


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app