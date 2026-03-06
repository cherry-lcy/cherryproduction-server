from flask_restful import Resource
from flask import request
from services.songs import SongsServices
from models.songs import SongsModel
from services.tags import TagsServices

class SongsResources(Resource):
    def get(self, id):
        song_model = SongsServices().get_song_by_id(id)
        if song_model:
            return song_model.serialize()
        else:
            return {"error": f"Song (id: {id}) is not found."}, 404
        
    def post(self, id):
        song_model = SongsServices().get_song_by_id(id)
        if song_model:
            add_count = SongsServices().add_play_count(id)
            if add_count:
                return {"message": "success"}, 200
            else: 
                return {"error": f"Fail to add count."}, 400
        else:
            return {"error": f"Song (id: {id}) is not found."}, 404
        
    def put(self, id):
        try:
            new_song = request.json

            if new_song:
                new_title = new_song.get("title", None)
                new_artist = new_song.get("artist", None)
                new_release_date = new_song.get("release_date", None)
                new_audio_url = new_song.get("audio_url", None)
                new_video_url = new_song.get("video_url", None)
                new_pdf_url = new_song.get("pdf_url", None)
                new_cover_url = new_song.get("cover_url", None)
                new_title = new_song.get("title", None)

                song_model = SongsModel(id=id, title=new_title, artist=new_artist, release_date=new_release_date, audio_url=new_audio_url, video_url=new_video_url, pdf_url=new_pdf_url, cover_url=new_cover_url)
                song_model = SongsServices().update_song(song_model)

                return song_model.serialize()
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    def delete(self, id):
        try:
            deleted_song = SongsServices().delete_song(id)
            if deleted_song:
                return 200
            else:
                return {"error": f"Fail to delete song (id: {id})"}, 400
        except Exception as err:
            return {"error": f"{err}"}, 400
        
