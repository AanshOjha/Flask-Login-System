import datetime
import os
import secrets
from flask import render_template, flash, redirect, request, send_from_directory, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from flaskalbum.models import Photo, User
from flaskalbum.utils import send_reset_email
from flaskalbum import app, db
from werkzeug.utils import secure_filename
# Create an instance of the User class from models.py
user = User()

# Route for the home page (login page)
@app.route('/')
def index(): 
    return redirect(url_for('login'))

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
        if User.authenticate_user(username, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login')

@app.route('/home')
@login_required
def home():
    name = current_user.name
    
    # Get all photos for current user with their details
    photo_details = Photo.query.filter_by(user_id=current_user.id).all()
    
    # Create a list of photo objects with both details and URLs
    photos = []
    for photo in photo_details:
        photo_data = {
            'id': photo.id,
            'url': url_for('serve_photo', filename=photo.filename),
            'title': photo.title,
            'description': photo.description,
            'location': photo.location,
            'tags': photo.tags,
            'upload_date': photo.upload_date,
            'is_favorite': photo.is_favorite
        }
        photos.append(photo_data)

    if request.method == 'POST':
        if 'edit_details' in request.form:
            print('home fine!')
            return url_for('edit_photo', photo_id=photo.id)
    
    return render_template('home.html', title='Home', name=name, photos=photos)

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
            logout_user()
            return redirect('/')

    # Handle GET request (display profile page)
    name = user.name
    email = user.email
    return render_template('profile.html', title='Profile', username=current_user.username, email=email, name=name)

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# ========================================================================================================
@app.route('/uploads/<filename>')
def serve_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'photo' not in request.files:
        return redirect(url_for('home'))

    photo = request.files['photo']
    if photo.filename == '':
        return redirect(url_for('home'))

    # Generate unique filename
    filename = secure_filename(f"{current_user.id}_{secrets.token_hex(10)}_{photo.filename}")
    
    # Save photo details to database
    new_photo = Photo(
        filename=filename,
        title=request.form['title'],
        description=request.form['description'],
        location=request.form['location'],
        tags=request.form['tags'],
        user_id=current_user.id
    )
    
    try:
        db.session.add(new_photo)
        db.session.commit()
        # Save the actual file
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], new_photo.filename))
        flash('Photo uploaded successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error uploading photo.', 'error')
        print(e)  # For debugging

    return redirect(url_for('home'))

@app.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('home'))
    
    # Delete file from uploads folder
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
    # Delete database record
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted successfully!', 'success')
    return redirect(url_for('home'))