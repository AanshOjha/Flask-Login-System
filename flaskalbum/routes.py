from flask import render_template, flash, redirect, request, session, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from flaskalbum.models import User
from flaskalbum.utils import send_reset_email
from flaskalbum import app, db
# Create an instance of the User class from models.py
user = User()

# Route for the home page (login page)
@app.route('/')
def index(): 
    return render_template('login.html', title='Login')

# Route for user registration
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Retrieve user registration form data
        data = {
            'name' : request.form['name'], # Input fields have these names
            'email' : request.form['email'],
            'username' : request.form['username'],
            'password' : request.form['password']
        }

        # Call create_user_user method to handle user registration
        
        # display message whether create_user is success or failed
        message = user.create_user(data)
        # danger and success for bootstrap styles
        flash(message, 'danger' if 'error' in message.lower() else 'success')
        if 'success' in message.lower():
            return redirect('/')

    # Render the registration form for GET requests
    return render_template('register.html', title='Create Account')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if User.authenticate_user(username, password):  # This is the correct method from Flask-Bcrypt
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login')

@app.route('/home')
@login_required
def home():
    # Use current_user instead of session
    name = current_user.name
    return render_template('index.html', title='Home', name=name)

# Route for user logout
@app.route('/logout')
def logout():
    # Remove the username from the session and redirect to the home page
    logout_user()
    return redirect('/')

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'error')
            return redirect(url_for('reset_request'))
            
        user = User.query.filter_by(email=email).first()
        print(user)
        
        # Always show the same message whether user exists or not
        # This prevents email enumeration attacks
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        
        if user:
            try:
                print(user.email)
                send_reset_email(user)
            except Exception as e:
                # Log the error but don't expose it to the user
                current_app.logger.error(f"Failed to send reset email: {str(e)}")
                
        return redirect(url_for('login'))
        
    return render_template('reset_request.html', title='Reset Password')

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # Verify the reset token
    email_from_token = user.verify_reset_token(token)
    
    # Check if the token is invalid or expired
    if email_from_token is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect('/')
    
    # Handle POST request for password reset
    if request.method == 'POST':
        try:
            # Retrieve and update the user's password
            password = request.form['password']
            if password:
                user.update_password(email_from_token, password)

                # Display a success message and redirect to the login page
                flash('Your password has been updated! You are now able to log in', 'success')
                return redirect('/login')
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password update failed: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    # Render the password reset form for GET requests
    return render_template('reset_token.html', title='Reset Password')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == 'POST':
        if 'update_profile' in request.form:
            # Get the updated info from the form
            update_username = request.form['username']
            name = request.form['name']
            email = request.form['email']

            # Update the info in DB and give message
            
            message = user.update_info(current_user.username, update_username, name, email)
            flash(message, 'info')

            # Update username present in session_id
            current_user.username = update_username

            # Get name from username and use in website
            name = user.name
            email = user.email
            return render_template('profile.html', title='Profile', username=current_user.username, email=email, name=name)
        
        elif 'delete_acc' in request.form:
            message = user.delete_account(current_user.username)
            flash(message, 'danger')
            session.pop('username', None)
            return redirect('/')

    # Handle GET request (display profile page)
    name = user.name
    email = user.email
    return render_template('profile.html', title='Profile', username=current_user.username, email=email, name=name)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# ========================================================================================================

