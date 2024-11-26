from datetime import datetime, timedelta
import os
from flask_login import UserMixin
from flaskalbum import app
import jwt

# Replace 'db' with your SQLAlchemy instance import
from flaskalbum import db, bcrypt
USER_INFO_TABLE = os.getenv('USER_INFO_TABLE')
PHOTO_INFO_TABLE = os.getenv('PHOTO_INFO_TABLE')

class User(db.Model, UserMixin):
    #User model for handling authentication and user management.
    __tablename__ = USER_INFO_TABLE  # Replace with your table name if different

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255))

    # Relationship with photos (one-to-many) - Keep if you need it
    photos = db.relationship('Photo', backref='user', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def create_user(data):
        # Create a new user from registration data.
        if User.find_by_username(data['username']):
            return 'Username already exists!'
        if User.find_by_email(data['email']):
            return 'Email address already exists!'

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            name=data['name'],
            email=data['email'],
            username=data['username'],
            password=hashed_password
        )

        if new_user.save_to_db():
            return 'Account created successfully. You can now log in.'
        return 'Something went wrong. Please try again later.'

    @classmethod
    def authenticate_user(cls, username, password):
        #Authenticate user with username/email and password.
        user = cls.query.filter(
            (cls.username == username) | (cls.email == username)
        ).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None

    def get_reset_token(self, expires_sec=600):
        #Generate a timed JWT token for password reset.
        expiration_time = (datetime.now() + timedelta(seconds=expires_sec)).isoformat()
        payload = {
            'email': self.email,
            'expiration': expiration_time
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        #Verify the reset token and return user email if valid.
        try:
            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            email = payload['email']
            print(email)
            expiration = datetime.strptime(payload['expiration'], '%Y-%m-%dT%H:%M:%S.%f')
            print(expiration)
            print(datetime.now())
            if expiration < datetime.now():
                return None
            
            return email
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def update_password(cls, email, password):
        #Update user password.
        user = cls.query.filter_by(email=email).first()
        if user:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            return True
        return False

    def update_info(self, username, update_username, name, email):
        #Update user information.
        try:
            user = User.query.filter_by(username=username).first()
            user.username = update_username
            user.name = name
            user.email = email
            db.session.commit()
            return 'Information updated successfully.'
        except Exception as e:
            db.session.rollback()
            print(e)
            return 'Failed to update information.'

    def profile_info(self, username, profile_photo):
        #Update user profile photo.
        try:
            user = User.query.filter_by(username=username).first()
            user.profile_photo = profile_photo
            db.session.commit()
            return 'Profile photo updated successfully.'
        except Exception as e:
            db.session.rollback()
            print(e)
            return 'Failed to update profile photo.'

    def delete_account(self, username):
        #Delete user account.
        try:
            user_to_delete = User.query.filter_by(username=username).first()
            db.session.delete(user_to_delete)
            db.session.commit()
            return 'Account deleted successfully.'
        except Exception as e:
            db.session.rollback()
            print(e)
            return 'Failed to delete account.'
        
    # When printing the object, return the user's username, email, and name
    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}', name='{self.name}, profile_photo='{self.profile_photo}')"

# ===========================================================================

# Database Model (using SQLAlchemy)
class Photo(db.Model):
    __tablename__ = PHOTO_INFO_TABLE

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.now().astimezone())
    user_id = db.Column(db.Integer, db.ForeignKey(f'{USER_INFO_TABLE}.id'), nullable=False)
    
    # Add these fields to make it more impressive
    location = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'