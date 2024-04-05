from datetime import datetime, timedelta
from flaskalbum import mysql, bcrypt, app
import jwt
from jwt import encode, decode
from envconfig import FULLSTACK_CRED_TABLE

class User:
    # Method to register a new user in the database
    def register_user(self, name, email, username, password):
        cursor = mysql.connection.cursor()

        # Check if the username or email already exists in the database
        cursor.execute(f"SELECT * FROM {FULLSTACK_CRED_TABLE} WHERE username = %s", (username,))
        user_with_username = cursor.fetchone()
        cursor.execute(f"SELECT * FROM {FULLSTACK_CRED_TABLE} WHERE email = %s", (email,))
        user_with_email = cursor.fetchone()

        if user_with_username:
            return 'Username already exists!'
        elif user_with_email:
            return 'Email address already exists!'
        else:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the user data into the database
            cursor.execute(f"INSERT INTO {FULLSTACK_CRED_TABLE} (name, email, username, password) VALUES (%s, %s, %s, %s)",
                           (name, email, username, hashed_password))
            mysql.connection.commit()
            cursor.close() 

            return 'Account created successfully. You can now log in.'
        
    # Method for login attempt by user    
    def authenticate_user(self, username, password):
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT username, password FROM {FULLSTACK_CRED_TABLE} WHERE username = %s OR email = %s", (username, username))
        user_row = cursor.fetchone()
        cursor.close()
    
        if user_row and bcrypt.check_password_hash(user_row[1], password):
            return user_row[0]
        else:
            return None

    # Method to generate a JWT token with an expiration time
    def get_reset_token(self, expires_sec=600):
        # Generates a JWT token with an expiration time.
        payload = {
            "email": self.email,
            "expiration": str(datetime.utcnow() + timedelta(seconds=expires_sec))
        }

        token = jwt.encode(payload, app.config["SECRET_KEY"])
        return token

    # Static method to verify the validity of a reset token and if valid, return email from it
    @staticmethod
    def verify_reset_token(token):
        try:
            # Decode the token and extract email and expiration time
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
            email = payload['email']
            expiration = datetime.strptime(payload['expiration'], '%Y-%m-%d %H:%M:%S.%f')
            
            # Check if the token has expired
            if expiration < datetime.utcnow():
                return None
            
            return email
            
        except jwt.ExpiredSignatureError:
            # Handle expired token
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None
        
    # Static method returning user data from email entered in reset password
    @staticmethod
    def get_user_by_email(email):
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM {FULLSTACK_CRED_TABLE} WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        return user_data

    # Static method to update password by taking email and password
    @staticmethod
    def update_password(email, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute(f"UPDATE {FULLSTACK_CRED_TABLE} SET password = %s WHERE email = %s", (hashed_password, email))
        mysql.connection.commit()
        cursor.close()
        
    # Representation of User object for debugging and logging
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}', '{self.name}')"
    
    # Method to get user details from username
    def user_details(self, username):
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT name, email FROM {FULLSTACK_CRED_TABLE} WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        return user_data
    
    # Method to update info by a form in profile page
    def update_info(self, username, update_username, name, email):
        cursor = mysql.connection.cursor()
        cursor.execute(f"UPDATE {FULLSTACK_CRED_TABLE} SET username=%s, name=%s, email=%s WHERE username=%s", (update_username, name, email, username))
        mysql.connection.commit()
        cursor.close()
        return 'Information updated successfully.'
    
    # Method to delete account by taking username from session
    def delete_acc(self, username):
        cursor = mysql.connection.cursor()
        cursor.execute(f"DELETE FROM {FULLSTACK_CRED_TABLE} WHERE username=%s", (username,))
        mysql.connection.commit()
        cursor.close()
        return 'Account deleted successfully.'