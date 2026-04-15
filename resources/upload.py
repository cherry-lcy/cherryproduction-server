import time
from flask_restful import Resource
import cloudinary.utils
import os
from flask import jsonify, request
from utils.auth import admin_required

class UploadResource(Resource):
    @admin_required
    def get(self):
        timestamp = int(time.time())
        folder = request.args.get('folder', 'music_site')
        
        params = {
            'timestamp': timestamp,
            'folder': folder,
        }
        
        signature = cloudinary.utils.api_sign_request(
            params,
            os.environ.get('CLOUDINARY_API_SECRET')
        )
        
        return jsonify({
            'signature': signature,
            'timestamp': timestamp,
            'api_key': os.environ.get('CLOUDINARY_API_KEY'),
            'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'folder': 'music_site'
        })