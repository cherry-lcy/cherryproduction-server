import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    if os.environ.get('FLASK_ENV') == 'production':
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        if database_url and 'neon.tech' in database_url and 'sslmode' not in database_url:
            if '?' in database_url:
                database_url += '&sslmode=require'
            else:
                database_url += '?sslmode=require'
        
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Cherry5052005@localhost/Web_Ex"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 300,
        'pool_pre_ping': True, 
    }
    
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')