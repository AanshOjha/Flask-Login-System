from flask import Blueprint, render_template, flash, redirect, request, session, url_for, current_app
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
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Retrieve user login form data
        username = request.form['username']
        password = request.form['password']

        authenticated_user = user.authenticate_user(username, password)

        # Check if the user exists and the password is correct
        if authenticated_user:
            # Store the username in the session and redirect to the home page
            session['username'] = authenticated_user.username
            return redirect('/home')
        else:
            # Display an error message for unsuccessful login attempts
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect('/')
        
    # Render the login page for GET requests
    return render_template('login.html', title='Login')

# Route for the home page after successful login
@app.route('/home')
def home():
    # Check if the user is logged in, if not, redirect to the login page
    if 'username' in session:
        # Get name from username and use in website
        user = User.query.filter_by(username=session['username']).first()
        print(user)
        name = user.name
        return render_template('index.html', title='Home', name=name)
    else:
        return redirect('/')

# Route for user logout
@app.route('/logout')
def logout():
    # Remove the username from the session and redirect to the home page
    session.pop('username', None)
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
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            if 'update_profile' in request.form:
                # Get the updated info from the form
                update_username = request.form['username']
                name = request.form['name']
                email = request.form['email']

                # Update the info in DB and give message
                
                message = user.update_info(session['username'], update_username, name, email)
                flash(message, 'info')

                # Update username present in session_id
                session['username'] = update_username

                # Get name from username and use in website
                name = user.name
                email = user.email
                return render_template('profile.html', title='Profile', username=session['username'], email=email, name=name)

            elif 'delete_acc' in request.form:
                message = user.delete_account(session['username'])
                flash(message, 'danger')
                session.pop('username', None)
                return redirect('/')

        # Handle GET request (display profile page)
        name = user.name
        email = user.email
        return render_template('profile.html', title='Profile', username=session['username'], email=email, name=name)
    
    else:
        return redirect('/')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404