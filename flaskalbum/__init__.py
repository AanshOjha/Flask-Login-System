from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
bcrypt = Bcrypt(app)
mysql = MySQL(app)

# Fetch environment variables 
EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PASS = os.getenv('EMAIL_PASS')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
FULLSTACK_DB = os.getenv('FULLSTACK_DB')
FULLSTACK_CRED_TABLE = os.getenv('FULLSTACK_CRED_TABLE')

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD

# Interact with the database
with app.app_context():
    mycursor = mysql.connection.cursor() 
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {FULLSTACK_DB}")
    mycursor.execute(f"USE {FULLSTACK_DB}")
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {FULLSTACK_CRED_TABLE} (name VARCHAR(120), email VARCHAR(120), username VARCHAR(120), password VARCHAR(120))")
    mycursor.close()

# MySQL Configuration 
app.config['MYSQL_DB'] = FULLSTACK_DB

from flaskalbum import routes