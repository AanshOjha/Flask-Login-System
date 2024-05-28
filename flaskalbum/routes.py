from flask import render_template, request, redirect, session, flash
from flaskalbum import app
from flaskalbum.models import User
from flaskalbum.utils import send_reset_email, send_otp_email, otp

# Create an instance of the User class from models.py
user = User()

# Route for the home page (login page)
@app.route('/')
def index(): 
    return render_template('login.html', title='Login')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve user registration form data
        name = request.form['name'] # Input fields have these names
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Call register_user method to handle user registration
        # display message whether register is success or failed
        message = user.register_user(name, email, username, password)
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
            session['username'] = authenticated_user
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
        user_data = user.user_details(session['username'])
        name = user_data[0]
        return render_template('index.html', title='Home', name=name)
    else:
        return redirect('/')

# Route for user logout
@app.route('/logout')
def logout():
    # Remove the username from the session and redirect to the home page
    session.pop('username', None)
    return redirect('/')

# Route for initiating a password reset request
@app.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        if email:
            user_data = user.get_user_by_email(email)

            # If no user found with the provided email, display a warning message
            if user_data is None:
                flash('No user found with that email address.', 'warning')
                return redirect('/reset_password')

            # Send the password reset email
            user.email = user_data[1]
            send_reset_email(user)

            # Display a success message and redirect to the login page
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect('/login')
        
    # Render the password reset request form for GET requests
    return render_template('reset_request.html', title='Forgot Password')

# Route for handling password reset with the provided token
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
        # Retrieve and update the user's password
        password = request.form['password']
        if password:
            user.update_password(email_from_token, password)

            # Display a success message and redirect to the login page
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect('/login')
    
    # Render the password reset form for GET requests
    return render_template('reset_token.html', title='Reset Password')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.route('/contact')
def contact():
    # Check if the user is logged in, if not, redirect to the login page
    if 'username' in session:
        return render_template('contact.html', title='Contact')
    else:
        return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
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

                # Display updated info in the form
                user_data = user.user_details(session['username'])
                name = user_data[0]
                email = user_data[1]
                return render_template('profile.html', title='Profile', username=session['username'], email=email, name=name)

            elif 'delete_acc' in request.form:
                message = user.delete_acc(session['username'])
                flash(message, 'danger')
                session.pop('username', None)
                return redirect('/')

        # Handle GET request (display profile page)
        user_data = user.user_details(session['username'])
        name = user_data[0]
        email = user_data[1]
        return render_template('profile.html', title='Profile', username=session['username'], email=email, name=name)
    
    else:
        return redirect('/')

@app.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        email = request.form['email']
        if email:
            user_data = user.get_user_by_email(email)

            # If no user found with the provided email, display a warning message
            if user_data is None:
                flash('No user found with that email address.', 'warning')
                return redirect('/send_otp')

            # Send the password reset email
            user.email = user_data[1]
            send_otp_email(user)

            flash('An OTP has been sent to your email.', 'success')
            return redirect('/verify_otp')
    return render_template('otp_send.html', title='Reset Password')     

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method=='POST':
        user_otp = int(request.form['user_otp'])
        if user_otp==otp:
            flash('Authenticated successfully!', 'success')

            token = user.get_reset_token()
            return redirect(f'reset_password/{token}')
        else:
            flash('Invalid OTP, try again', 'danger')
            return redirect('/verify_otp')
    return render_template('otp_verify.html', title='Verify OTP')