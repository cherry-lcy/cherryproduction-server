import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    if os.environ.get('FLASK_ENV') == 'production':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:Cherry5052005@localhost/Web_Ex"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')