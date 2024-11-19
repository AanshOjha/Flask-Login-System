from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# Load environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
PHOTO_ALBUM_DB = os.getenv('PHOTO_ALBUM_DB')
USER_INFO_TABLE = os.getenv('USER_INFO_TABLE')
PHOTO_INFO_TABLE = os.getenv('PHOTO_INFO_TABLE')
EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PASS = os.getenv('EMAIL_PASS')

# Configure MySQL
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_ROOT_PASSWORD
app.config['UPLOAD_FOLDER'] = '/uploads'    # mistakenly wrote os.path.join('/upload'), should be '/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{MYSQL_USER}:"
    f"{MYSQL_ROOT_PASSWORD}@"
    f"{MYSQL_HOST}/"
    f"{PHOTO_ALBUM_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mysql = MySQL(app)
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# Configure login manager
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models
from flaskalbum.models import Photo, User

# User loader callback
@login_manager.user_loader
def load_user(id):
    if id is None:
        return None
    try:
        return User.query.get(int(id))
    except (ValueError, TypeError):
        return None

# Create database tables
with app.app_context():
    mycursor = mysql.connection.cursor() 
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {PHOTO_ALBUM_DB}")
    mycursor.execute(f"USE {PHOTO_ALBUM_DB}")
    mycursor.close()
    db.create_all()

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Photo, db.session))

# Import routes
from flaskalbum import routes