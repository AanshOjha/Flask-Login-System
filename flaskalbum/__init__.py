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
PHOTO_ALBUM_DB = os.getenv('PHOTO_ALBUM_DB')
USER_INFO_TABLE = os.getenv('USER_INFO_TABLE')

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD
app.config['UPLOAD_FOLDER'] = '/uploads'    # mistakenly wrote os.path.join('/upload'), should be '/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Interact with the database
with app.app_context():
    mycursor = mysql.connection.cursor() 
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {PHOTO_ALBUM_DB}")
    mycursor.execute(f"USE {PHOTO_ALBUM_DB}")
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {USER_INFO_TABLE} (name VARCHAR(120), email VARCHAR(120), username VARCHAR(120), password VARCHAR(120))")
    mycursor.close()

# MySQL Configuration 
app.config['MYSQL_DB'] = PHOTO_ALBUM_DB

from flaskalbum import routes