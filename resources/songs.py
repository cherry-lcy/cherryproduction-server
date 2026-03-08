from flask_restful import Resource
from flask import request
from services.songs import SongsServices
from models.songs import SongsModel
from services.upload import CloudinaryService

class SongsResources(Resource):
    def get(self):
        songs = SongsServices().get_all_songs()
        
        songs_with_covers = []
        for song in songs:
            song_data = song.serialize()
            
            if song_data.get('cover_url'):
                cover_info = CloudinaryService().get_file_info_by_url(song_data['cover_url'])
                song_data['cover'] = {
                    'url': cover_info.get('url') if cover_info else None,
                    'bytes': cover_info.get('bytes') if cover_info else None,
                    'width': cover_info.get('width'),
                    'height': cover_info.get('height')
                }
            else:
                song_data['cover'] = None
            
            songs_with_covers.append(song_data)
        
        return {
            "songs": songs_with_covers,
            "total": len(songs_with_covers)
        }, 200
    
    def post(self):
        try:
            new_title = request.form.get("title")
            new_artist = request.form.get("artist")
            new_type = request.form.get("type")
            new_release_date = request.form.get("release_date")
            new_video_url = request.form.get("video_url")

            audio = request.files.get("audio")
            pdf = request.files.get("pdf")
            cover = request.files.get("cover")

            cloudinary_service = CloudinaryService()
            
            audio_info = cloudinary_service.upload_audio(
                audio_file=audio, 
                title=new_title, 
                artist=new_artist
            )
            
            pdf_info = cloudinary_service.upload_pdf(
                pdf_file=pdf, 
                title=new_title, 
                artist=new_artist
            )
            
            cover_info = cloudinary_service.upload_image(
                image_file=cover, 
                title=new_title
            )

            song_model = SongsModel(
                title=new_title, 
                artist=new_artist, 
                type=new_type,
                release_date=new_release_date, 
                audio_url=audio_info["url"], 
                video_url=new_video_url, 
                pdf_url=pdf_info["url"], 
                cover_url=cover_info["url"]
            )
            
            song_model = SongsServices().add_song(song_model)
            
            song_data = song_model.serialize()
            song_data['cover'] = {
                'url': cover_info['url'],
                'bytes': cover_info['bytes'],
                'width': cover_info.get('width'),
                'height': cover_info.get('height')
            }

            return {
                "song": song_data
            }, 200 

        except Exception as err:
            return {"error": str(err)}, 500

class SongResources(Resource):
    def get(self, id):
        song_model = SongsServices().get_song_by_id(id)

        if song_model:
            SongsServices().add_play_count(id)

            cloudinary_service = CloudinaryService()
            
            song_data = song_model.serialize()
            
            if song_model.audio_url:
                audio_info = cloudinary_service.get_file_info_by_url(song_model.audio_url)
                song_data['audio'] = {
                    'bytes': audio_info.get('bytes') if audio_info else None,
                    'duration': audio_info.get('duration') if audio_info else None,
                    'format': audio_info.get('format') if audio_info else None
                }
            
            if song_model.pdf_url:
                pdf_info = cloudinary_service.get_file_info_by_url(song_model.pdf_url)
                song_data['pdf'] = {
                    'bytes': pdf_info.get('bytes') if pdf_info else None,
                    'format': pdf_info.get('format') if pdf_info else None
                }
            
            if song_model.cover_url:
                cover_info = cloudinary_service.get_file_info_by_url(song_model.cover_url)
                song_data['cover'] = {
                    'url': cover_info.get('url') if cover_info else None,
                    'bytes': cover_info.get('bytes') if cover_info else None,
                    'width': cover_info.get('width'),
                    'height': cover_info.get('height')
                }

            return song_data, 200
        else:
            return {"error": f"Song (id: {id}) is not found."}, 404
        
    def put(self, id):
        """
        update song information
        """
        try:
            new_song = request.json

            if new_song:
                new_title = new_song.get("title", None)
                new_artist = new_song.get("artist", None)
                new_type = new_song.get("type", None)
                new_release_date = new_song.get("release_date", None)
                new_audio_url = new_song.get("audio_url", None)
                new_video_url = new_song.get("video_url", None)
                new_pdf_url = new_song.get("pdf_url", None)
                new_cover_url = new_song.get("cover_url", None)
                new_title = new_song.get("title", None)

                song_model = SongsModel(id=id, title=new_title, artist=new_artist, type=new_type, release_date=new_release_date, audio_url=new_audio_url, video_url=new_video_url, pdf_url=new_pdf_url, cover_url=new_cover_url)
                song_model = SongsServices().update_song(song_model)

                return {
                    "song": song_model.serialize()
                }, 200            
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    def delete(self, id):
        try:
            deleted_song = SongsServices().delete_song(id)
            if deleted_song:
                return {"message": "success"}, 200
            else:
                return {"error": f"Fail to delete song (id: {id})"}, 400
        except Exception as err:
            return {"error": f"{err}"}, 400
        
class SearchResources(Resource):
    def get(self):
        title = request.args.get('title', '')
        artist = request.args.get('artist', '')
        song_type = request.args.get('type', '')
        keyword = request.args.get('q', '')
        
        sort_by = request.args.get('sort_by', 'release_date')
        order = request.args.get('order', 'desc')
        limit = request.args.get('limit', None, type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        songs = SongsServices().get_all_songs()
        cloudinary_service = CloudinaryService()
        
        filtered_songs = []
        for song in songs:
            song_data = song.serialize()
            
            if title and title.lower() not in song_data.get('title', '').lower():
                continue
            if artist and artist.lower() not in song_data.get('artist', '').lower():
                continue
            if song_type and song_type.lower() != song_data.get('type', '').lower():
                continue
            if keyword:
                keyword_lower = keyword.lower()
                title_match = keyword_lower in song_data.get('title', '').lower()
                artist_match = keyword_lower in song_data.get('artist', '').lower()
                type_match = keyword_lower in song_data.get('type', '').lower()
                if not (title_match or artist_match or type_match):
                    continue
            
            if song_data.get('cover_url'):
                cover_info = cloudinary_service.get_file_info_by_url(song_data['cover_url'])
                song_data['cover'] = {
                    'url': cover_info.get('url') if cover_info else None,
                    'bytes': cover_info.get('bytes') if cover_info else None
                }
            
            filtered_songs.append(song_data)
        
        allowed_sort_fields = ['title', 'artist', 'release_date']
        if sort_by not in allowed_sort_fields:
            sort_by = 'release_date'
        
        reverse = (order.lower() == 'desc')
        filtered_songs.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_songs = filtered_songs[start:end]
        
        if limit and limit > 0:
            paginated_songs = filtered_songs[:limit]
        
        return {
            "success": True,
            "data": {
                "total": len(filtered_songs),
                "page": page,
                "per_page": per_page,
                "total_pages": (len(filtered_songs) + per_page - 1) // per_page,
                "songs": paginated_songs
            },
            "filters": {
                "title": title,
                "artist": artist,
                "type": song_type,
                "keyword": keyword
            },
            "sort": {
                "by": sort_by,
                "order": order
            }
        }, 200