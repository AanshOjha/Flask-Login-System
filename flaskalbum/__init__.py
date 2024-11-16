from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
PHOTO_ALBUM_DB = os.getenv('PHOTO_ALBUM_DB')
USER_INFO_TABLE = os.getenv('USER_INFO_TABLE')
EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PASS = os.getenv('EMAIL_PASS')

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{MYSQL_USER}:"
    f"{MYSQL_ROOT_PASSWORD}@"
    f"{MYSQL_HOST}/"
    f"{PHOTO_ALBUM_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
mysql = MySQL(app)

# Initialize Flask extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models here to avoid circular imports
from flaskalbum.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    mycursor = mysql.connection.cursor() 
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {PHOTO_ALBUM_DB}")
    mycursor.execute(f"USE {PHOTO_ALBUM_DB}")
    mycursor.close()
    db.create_all()

# create_user blueprints
from flaskalbum import routes