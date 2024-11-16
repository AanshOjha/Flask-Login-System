from datetime import datetime, timedelta
from flask_login import UserMixin
from flask import current_app
import jwt

# Replace 'db' with your SQLAlchemy instance import
from flaskalbum import USER_INFO_TABLE, db, bcrypt

class User(db.Model, UserMixin):
    #User model for handling authentication and user management.
    __tablename__ = f'{USER_INFO_TABLE}'  # Replace with your table name if different

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relationship with photos (one-to-many) - Keep if you need it
    # photos = db.relationship('Photo', backref='user', lazy=True, cascade='all, delete-orphan')

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
        payload = {
            'email': self.email,
            'exp': datetime.utcnow() + timedelta(seconds=expires_sec)
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        #Verify the reset token and return user email if valid.
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload['email']
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

    def update_info(self, update_username, name, email):
        #Update user information.
        try:
            self.username = update_username
            self.name = name
            self.email = email
            db.session.commit()
            return 'Information updated successfully.'
        except Exception as e:
            db.session.rollback()
            return 'Failed to update information.'

    def delete_account(self):
        #Delete user account.
        try:
            db.session.delete(self)
            db.session.commit()
            return 'Account deleted successfully.'
        except Exception as e:
            db.session.rollback()
            return 'Failed to delete account.'

    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}')"