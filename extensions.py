from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS
from utils.access_logger import AccessLogger

ALLOWED_SORT_BY = ['release_date', 'title', 'artist', 'play_count']
ALLOWED_ORDERS = ['asc', 'desc']
ALLOWED_TYPES = ['Transcription', 'Arrangement', 'Original', 'Cover']
MAX_PER_PAGE = 50

db = SQLAlchemy()
cors = CORS()
api = Api()  
access_logger = AccessLogger()