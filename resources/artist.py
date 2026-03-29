from flask_restful import Resource
from flask import request
from services.songs import SongsServices

class ArtistsResource(Resource):
    def get(self):
        artists = SongsServices().get_all_artist()
        
        return {
            'artists': artists
        }, 200