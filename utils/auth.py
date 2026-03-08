from flask import request, session
from functools import wraps
import time
import os
import hashlib

def generate_token(password):
    hour_slot = str(int(time.time() / 3600))
    token_string = password + hour_slot
    return hashlib.md5(token_string.encode()).hexdigest()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        
        expected_token = generate_token(os.environ.get('ADMIN_PASSWORD'))
        
        if token != expected_token:
            return {"error": "Unauthorized"}, 401
        
        return f(*args, **kwargs)
    return decorated_function
