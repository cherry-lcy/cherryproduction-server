from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS
from utils.access_logger import AccessLogger

db = SQLAlchemy()
cors = CORS()
api = Api()  
access_logger = AccessLogger()