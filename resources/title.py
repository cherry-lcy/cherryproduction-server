from flask_restful import Resource
from flask import request
from services.songs import SongsServices

class TitlesResource(Resource):
    def get(self):
        title = SongsServices().get_all_title()
        
        return {
            'titles': title
        }, 200
    
class TitlesByArtistResource(Resource):
    def get(self, artist):
        title = SongsServices().get_all_title(artist=artist)
        
        return {
            'titles': title
        }, 200