import time
from flask_restful import Resource
import cloudinary.utils
import os
from flask import jsonify
from utils.auth import admin_required

class UploadResource(Resource):
    @admin_required
    def get(self):
        timestamp = int(time.time())
        
        params = {
            'timestamp': timestamp,
            'folder': 'music_site',
        }
        
        signature = cloudinary.utils.api_sign_request(
            params,
            os.environ.get('CLOUDINARY_API_SECRET')
        )
        
        return jsonify({
            'signature': signature,
            'timestamp': timestamp,
            'api_key': os.environ('CLOUDINARY_API_KEY'),
            'cloud_name': os.environ('CLOUDINARY_CLOUD_NAME'),
            'folder': 'music_site'
        })