import time
from flask_restful import Resource
from flask import request
from services.songs import SongsServices
from models.songs import SongsModel
from services.tags import TagsServices
from services.upload import CloudinaryService
from utils.auth import admin_required

class SongsResources(Resource):
    def get(self):
        songs = SongsServices().get_all_songs()
        
        songs_with_covers = []
        for song in songs:
            song_data = song.serialize()
            songs_with_covers.append(song_data)
        
        return {
            "songs": songs_with_covers,
            "total": len(songs_with_covers)
        }, 200
    
    @admin_required
    def post(self):
        try:
            new_title = request.form.get("title")
            new_title_zhcn = request.form.get("title_zhcn")
            new_title_zhhk = request.form.get("title_zhhk")
            new_artist = request.form.get("artist")
            new_type = request.form.get("type")
            new_release_date = request.form.get("release_date")
            new_video_url = request.form.get("video_url")
            new_audio_url = request.form.get("audio_url")
            new_pdf_url = request.form.get("pdf_url")
            new_cover_url = request.form.get("cover_url")

            song_model = SongsModel(
                title=new_title, 
                title_zhcn=new_title_zhcn,
                title_zhhk=new_title_zhhk,
                artist=new_artist, 
                type=new_type,
                release_date=new_release_date, 
                audio_url=new_audio_url, 
                video_url=new_video_url, 
                pdf_url=new_pdf_url, 
                cover_url=new_cover_url
            )
            
            song_model = SongsServices().add_song(song_model)
            
            song_data = song_model.serialize()

            return {
                "song": song_data
            }, 200 

        except Exception as err:
            return {"error": str(err)}, 500
        
    @admin_required
    def delete(self):
        try:
            del_song = request.json

            song = SongsServices().get_songs_by_title_and_artist(del_song.get("title"), del_song.get("artist"))

            if song:
                del_audio = CloudinaryService().delete_file_by_url(song.audio_url)
                del_pdf = CloudinaryService().delete_file_by_url(song.pdf_url)
                del_cover = CloudinaryService().delete_file_by_url(song.cover_url)

                deleted_song = SongsServices().delete_song(song.id)
                
                if del_audio and del_cover and del_pdf and deleted_song:
                    return {"message": "success"}, 200
            
            return {"error": f"Fail to delete song (id: {song.id})"}, 400
        except Exception as err:
            return {"error": f"{err}"}, 400

class SongResources(Resource):
    def get(self, id):
        song_model = SongsServices().get_song_by_id(id)

        if song_model:
            SongsServices().add_play_count(id)

            cloudinary_service = CloudinaryService()
            
            song_data = song_model.serialize()

            return {"data": song_data}, 200
        else:
            return {"error": f"Song (id: {id}) is not found."}, 404
        
    @admin_required
    def put(self, id):
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

                song_model = SongsModel(id=id, title=new_title, artist=new_artist, type=new_type, release_date=new_release_date, audio_url=new_audio_url, video_url=new_video_url, pdf_url=new_pdf_url, cover_url=new_cover_url)
                song_model = SongsServices().update_song(song_model)

                return {
                    "song": song_model.serialize()
                }, 200            
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    @admin_required
    def delete(self, id):
        try:
            song = SongsServices().get_song_by_id(id)

            del_audio = CloudinaryService().delete_file_by_url(song.audio_url)
            del_pdf = CloudinaryService().delete_file_by_url(song.pdf_url)
            del_cover = CloudinaryService().delete_file_by_url(song.cover_url)

            deleted_song = SongsServices().delete_song(id)
            if deleted_song and del_audio and del_pdf and del_cover:
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
        language = request.args.get('language', 'en')
        
        songs = SongsServices().get_all_songs()
        cloudinary_service = CloudinaryService()
        tags_service = TagsServices()
        
        filtered_songs = []
        for song in songs:
            song_data = song.serialize()
            
            if title:
                title_lower = title.lower()
                title_match = (
                    title_lower in song_data.get('title', '').lower() or
                    (song.title_zhcn and title_lower in song.title_zhcn.lower()) or
                    (song.title_zhhk and title_lower in song.title_zhhk.lower())
                )
                if not title_match:
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
                
                zhcn_match = song.title_zhcn and keyword_lower in song.title_zhcn.lower()
                zhhk_match = song.title_zhhk and keyword_lower in song.title_zhhk.lower()
                
                if not (title_match or artist_match or type_match or zhcn_match or zhhk_match):
                    continue
            
            tags = tags_service.get_tag_by_sid(song.id)
            song_data['tags'] = [tag.tag for tag in tags]
            
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
                "keyword": keyword,
                "language": language
            },
            "sort": {
                "by": sort_by,
                "order": order
            }
        }, 200

class LikeResources(Resource):
    def get(self, id):
        try:
            count = SongsServices().add_play_count(id, 0)
            return {"playCount": count}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    def post(self, id):
        try:
            count = SongsServices().add_play_count(id, 1)
            return {"playCount": count}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400

    def delete(self, id):
        try: 
            count = SongsServices().add_play_count(id, -1)
            return {"message":"success"}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400

class UploadAudioResource(Resource):
    @admin_required
    def post(self):
        try:
            audio_file = request.files.get('audio')
            title = request.form.get('title')
            artist = request.form.get('artist')
            
            if not audio_file:
                return {"error": "No audio file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            if not artist:
                return {"error": "Artist is required"}, 400
            
            cloudinary_service = CloudinaryService()
            result = cloudinary_service.upload_audio(audio_file, title, artist)
            
            if result:
                return {
                    "success": True,
                    "audio_url": result['url'],
                    "public_id": result['public_id'],
                    "duration": result['duration'],
                    "format": result['format'],
                    "bytes": result['bytes']
                }, 200
            else:
                return {"error": "Failed to upload audio"}, 500
        except Exception as err:
            return {"error": str(err)}, 500

class UploadImageResource(Resource):
    @admin_required
    def post(self):
        try:
            image_file = request.files.get('image')
            title = request.form.get('title')
            folder = request.form.get('folder', 'covers')
            
            if not image_file:
                return {"error": "No image file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            
            cloudinary_service = CloudinaryService()
            result = cloudinary_service.upload_image(image_file, title, folder)
            
            if result:
                return {
                    "success": True,
                    "image_url": result['url'],
                    "public_id": result['public_id'],
                    "width": result['width'],
                    "height": result['height'],
                    "format": result['format'],
                    "bytes": result['bytes']
                }, 200
            else:
                return {"error": "Failed to upload image"}, 500
        except Exception as err:
            return {"error": str(err)}, 500

class UploadPdfResource(Resource):
    @admin_required
    def post(self):
        try:
            pdf_file = request.files.get('pdf')
            title = request.form.get('title')
            
            if not pdf_file:
                return {"error": "No PDF file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            
            cloudinary_service = CloudinaryService()
            result = cloudinary_service.upload_image(pdf_file, title, "pdf")
            
            if result:
                return {
                    "success": True,
                    "pdf_url": result['url'],
                    "public_id": result['public_id'],
                    "format": result['format'],
                    "bytes": result['bytes']
                }, 200
            else:
                return {"error": "Failed to upload PDF"}, 500
        except Exception as err:
            return {"error": str(err)}, 500