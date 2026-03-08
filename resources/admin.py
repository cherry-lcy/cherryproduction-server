from flask_restful import Resource
from flask import request
import os
from utils.auth import generate_token

class AdminResource(Resource):
    def post(self):
        user = request.json
        username = user.get("username")
        password = user.get("password")

        if username == os.environ.get('ADMIN_USERNAME') and password == os.environ.get('ADMIN_PASSWORD'):
            token = generate_token(password)
            return {
                "status": "OK",
                "token": token,
                "expires_in": 3600
            }, 200
        
        return {"status": "error", "error": "Wrong password"}, 401