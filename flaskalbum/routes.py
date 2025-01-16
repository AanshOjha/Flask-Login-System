import os
import secrets
import uuid
from flask import json, render_template, flash, redirect, request, send_from_directory, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
import requests
from flaskalbum.models import Photo, User
from flaskalbum.utils import send_reset_email
from flaskalbum import app, db, client
from werkzeug.utils import secure_filename

GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

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
            'id' : uuid.uuid4().hex,
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
        if 'login' in request.form:    
            username = request.form['username']
            password = request.form['password']

            # Check if user exists and password is correct
            authenticated_user = User.authenticate_user(username, password)
            if authenticated_user:
                print("User authenticated successfully")
                print(authenticated_user)
                login_user(authenticated_user)
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        
        if 'oauth' in request.form:
            # Find the Google provider configuration
            google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]

            # Generate the URL to request access from Google's OAuth 2.0 server
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=f"{os.environ.get('WEBSITE_DOMAIN')}/login/callback", # request.base_url + "/callback",
                scope=["openid", "email", "profile"],
            )
            return redirect(request_uri)
    
    return render_template('login.html', title='Login')

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json())) 

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        profile_photo = userinfo_response.json()["picture"]
        name = userinfo_response.json()["name"]

        data = {
            'id': id,
            'name': name,
            'email': email,
            'profile_photo': profile_photo
        }

        user = User().oauth(data)
        print(user)
        login_user(user)
        return redirect(url_for('home'))
        
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    name = current_user.name
    print('variable' +app.config['UPLOAD_FOLDER'])
    
    # Get all photos for current user with their details
    photo_details = Photo.query.filter_by(user_id=current_user.id).all()
    
    # Create a list of photo objects with both details and URLs
    photos = []
    for photo in photo_details:
        if photo.filename:
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

@app.context_processor
def profile_display():
    if current_user.is_authenticated:
        # print('Password: ' + current_user.password)
        if current_user.password != None: # user is not oauth user
            profile_photo = ('/uploads/' + current_user.profile_photo) if current_user.profile_photo else None
        else: # user is oauth user
            profile_photo = current_user.profile_photo
        return dict(profile_photo=profile_photo)
    return {}

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(email=current_user.email).first()
    print(os.getcwd())
    if request.method == 'POST':
        if 'profile_photo' in request.files:
            if 'profile_photo' not in request.files:
                return redirect(url_for('profile'))

            profile_photo = request.files['profile_photo']
            if profile_photo.filename == '':
                return redirect(url_for('profile'))

            # Generate unique filename
            filename = secure_filename(f"{current_user.id}_profile_photo_{secrets.token_hex(10)}_{profile_photo.filename}")

            # Save the photo to the uploads folder
            try:
                cwd = os.getcwd()+'/'
                u_cwd = cwd.replace('\\', '/') + url_for('serve_photo', filename=user.profile_photo)
                os.remove(u_cwd)
            except Exception as e:
                # Log the error but don't expose it to the user
                current_app.logger.error(f"os.remove didn't worked: {str(e)}")
            profile_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            message = user.profile_info(current_user.username, filename)
            flash(message, 'info')
            return redirect(url_for('profile'))

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
    filename = user.profile_photo
    profile_photo = None
    if filename:   
        profile_photo = profile_display().get('profile_photo')
    return render_template('profile.html', title='Profile', username=current_user.username, email=email, name=name, profile_photo=profile_photo)

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

@app.route('/photo/<int:photo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        photo.title = request.form['title']
        photo.description = request.form['description']
        photo.location = request.form['location']
        photo.tags = request.form['tags']
        
        try:
            db.session.commit()
            flash('Photo details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating photo details.', 'error')
            current_app.logger.error(f"Error updating photo details: {str(e)}")
        
        return redirect(url_for('home'))
    return render_template('edit_photo.html', title='Edit Photo', photo=photo)