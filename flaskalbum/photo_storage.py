from flask import Flask, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

class PhotoStorage:
    def __init__(self, app):
        self.app = app
        # Create base upload directory
        self.upload_base = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(self.upload_base):
            os.makedirs(self.upload_base)
    
    def get_user_upload_path(self, username):
        """Create and return user-specific upload directory"""
        user_path = os.path.join(self.upload_base, username)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        return user_path
    
    def save_photo(self, file, username):
        """Save uploaded photo to user's directory"""
        if file.filename == '':
            return None, "No selected file"
            
        if file:
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            extension = os.path.splitext(original_filename)[1]
            new_filename = f"{uuid.uuid4()}{extension}"
            
            # Save file
            upload_path = self.get_user_upload_path(username)
            file_path = os.path.join(upload_path, new_filename)
            file.save(file_path)
            
            # Return metadata
            return {
                'filename': new_filename,
                'original_name': original_filename,
                'upload_date': datetime.now().isoformat(),
                'path': file_path
            }, None
            
        return None, "File upload failed"
    
    def get_user_photos(self, username):
        """Get list of all photos for a user"""
        user_path = self.get_user_upload_path(username)
        photos = []
        
        for filename in os.listdir(user_path):
            file_path = os.path.join(user_path, filename)
            if os.path.isfile(file_path):
                photos.append({
                    'filename': filename,
                    'upload_date': datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    ).isoformat()
                })
                
        return photos
    
    def get_photo(self, username, filename):
        """Retrieve a specific photo"""
        user_path = self.get_user_upload_path(username)
        return os.path.join(user_path, filename)
    
    def delete_photo(self, username, filename):
        """Delete a specific photo"""
        user_path = self.get_user_upload_path(username)
        file_path = os.path.join(user_path, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False