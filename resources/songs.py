# resources/song_resource.py
import time
import re
from flask_restful import Resource
from flask import request
from services.songs import SongsServices
from models.songs import SongsModel
from services.tags import TagsServices
from services.upload import CloudinaryService
from utils.auth import admin_required

# XSS Protection Utilities
def sanitize_input(value):
    """
    Sanitize user input to prevent XSS attacks.
    Removes dangerous HTML tags, attributes, and JavaScript protocols.
    """
    if not value or not isinstance(value, str):
        return value
    
    # Remove <script> tags and their content (including variations)
    value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <iframe> tags
    value = re.sub(r'<iframe.*?>.*?</iframe>', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <object> tags
    value = re.sub(r'<object.*?>.*?</object>', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <embed> tags
    value = re.sub(r'<embed.*?>', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove on* event attributes (onclick, onerror, onload, etc.)
    value = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    value = re.sub(r'javascript\s*:', '', value, flags=re.IGNORECASE)
    
    # Remove vbscript: protocol
    value = re.sub(r'vbscript\s*:', '', value, flags=re.IGNORECASE)
    
    # Remove data: protocol (used for base64 XSS)
    value = re.sub(r'data\s*:', '', value, flags=re.IGNORECASE)
    
    # Remove HTML comments that might contain malicious code
    value = re.sub(r'<!--.*?-->', '', value, flags=re.DOTALL)
    
    # Escape remaining HTML entities to be safe
    # Note: This is a basic escape, consider using a proper HTML escaper in production
    html_escape_table = {
        '"': '&quot;',
        "'": '&#x27;',
        '>': '&gt;',
        '<': '&lt;',
        '&': '&amp;',
    }
    value = ''.join(html_escape_table.get(c, c) for c in value)
    
    return value

def sanitize_dict(data):
    """
    Recursively sanitize all string values in a dictionary.
    """
    if not data:
        return data
    
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return sanitize_input(data)
    else:
        return data

ALLOWED_SORT_BY = ['release_date', 'title', 'artist', 'play_count']
ALLOWED_ORDERS = ['asc', 'desc']
ALLOWED_TYPES = ['Transcription', 'Arrangement', 'Original', 'Cover']
MAX_PER_PAGE = 50
MAX_QUERY_LENGTH = 200
MAX_TITLE_LENGTH = 200
MAX_ARTIST_LENGTH = 100

def validate_search_params(args):
    """
    Validate and sanitize search parameters.
    Returns (sanitized_params, error_message)
    """
    page = args.get('page', 1, type=int)
    per_page = args.get('per_page', 20, type=int)
    sort_by = args.get('sort_by', 'release_date')
    order = args.get('order', 'desc')
    artist = args.get('artist', '')
    title = args.get('title', '')
    type_filter = args.get('type', '')
    keyword = args.get('q', '')
    language = args.get('language', 'en')
    limit = args.get('limit', None, type=int)
    
    artist = sanitize_input(artist)
    title = sanitize_input(title)
    type_filter = sanitize_input(type_filter)
    keyword = sanitize_input(keyword)
    language = sanitize_input(language)
    
    if len(keyword) > MAX_QUERY_LENGTH:
        keyword = keyword[:MAX_QUERY_LENGTH]
    
    if len(artist) > MAX_ARTIST_LENGTH:
        artist = artist[:MAX_ARTIST_LENGTH]
    
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH]
    
    if sort_by not in ALLOWED_SORT_BY:
        sort_by = 'release_date'
    
    if order not in ALLOWED_ORDERS:
        order = 'desc'
    
    if type_filter and type_filter not in ALLOWED_TYPES:
        type_filter = ''
    
    if language not in ['en', 'zh-CN', 'zh-TW']:
        language = 'en'
    
    # Pagination validation
    if per_page < 1:
        per_page = 20
    if per_page > MAX_PER_PAGE:
        per_page = MAX_PER_PAGE
    
    if page < 1:
        page = 1
    
    if limit is not None and limit < 1:
        limit = None
    
    return {
        'page': page,
        'per_page': per_page,
        'sort_by': sort_by,
        'order': order,
        'artist': artist,
        'title': title,
        'type': type_filter,
        'keyword': keyword,
        'language': language,
        'limit': limit
    }, None


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
            new_title = sanitize_input(request.form.get("title"))
            new_title_zhcn = sanitize_input(request.form.get("title_zhcn"))
            new_title_zhhk = sanitize_input(request.form.get("title_zhhk"))
            new_artist = sanitize_input(request.form.get("artist"))
            new_type = sanitize_input(request.form.get("type"))
            new_release_date = sanitize_input(request.form.get("release_date"))
            new_video_url = sanitize_input(request.form.get("video_url"))
            new_audio_url = sanitize_input(request.form.get("audio_url"))
            new_pdf_url = sanitize_input(request.form.get("pdf_url"))
            new_cover_url = sanitize_input(request.form.get("cover_url"))
            
            if not new_title or not new_artist:
                return {"error": "Title and artist are required"}, 400
            
            if new_type and new_type not in ALLOWED_TYPES:
                return {"error": f"Invalid type. Allowed: {', '.join(ALLOWED_TYPES)}"}, 400

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
            # Sanitize input data
            del_song = request.json
            if del_song:
                del_song = sanitize_dict(del_song)

            song = SongsServices().get_songs_by_title_and_artist(
                del_song.get("title"), 
                del_song.get("artist")
            )

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
        # Validate ID is a positive integer
        try:
            song_id = int(id)
            if song_id < 1:
                return {"error": "Invalid song ID"}, 400
        except (ValueError, TypeError):
            return {"error": "Invalid song ID format"}, 400
        
        song_model = SongsServices().get_song_by_id(song_id)

        if song_model:
            SongsServices().add_play_count(song_id)

            cloudinary_service = CloudinaryService()
            
            song_data = song_model.serialize()

            return {"data": song_data}, 200
        else:
            return {"error": f"Song (id: {song_id}) is not found."}, 404
        
    @admin_required
    def put(self, id):
        try:
            # Validate ID
            try:
                song_id = int(id)
                if song_id < 1:
                    return {"error": "Invalid song ID"}, 400
            except (ValueError, TypeError):
                return {"error": "Invalid song ID format"}, 400
            
            # Get and sanitize input
            new_song = request.json
            if new_song:
                new_song = sanitize_dict(new_song)
            else:
                return {"error": "No data provided"}, 400

            if new_song:
                new_title = new_song.get("title", None)
                new_artist = new_song.get("artist", None)
                new_type = new_song.get("type", None)
                new_release_date = new_song.get("release_date", None)
                new_audio_url = new_song.get("audio_url", None)
                new_video_url = new_song.get("video_url", None)
                new_pdf_url = new_song.get("pdf_url", None)
                new_cover_url = new_song.get("cover_url", None)
                
                # Validate type if provided
                if new_type and new_type not in ALLOWED_TYPES:
                    return {"error": f"Invalid type. Allowed: {', '.join(ALLOWED_TYPES)}"}, 400

                song_model = SongsModel(
                    id=song_id, 
                    title=new_title, 
                    artist=new_artist, 
                    type=new_type, 
                    release_date=new_release_date, 
                    audio_url=new_audio_url, 
                    video_url=new_video_url, 
                    pdf_url=new_pdf_url, 
                    cover_url=new_cover_url
                )
                song_model = SongsServices().update_song(song_model)

                return {
                    "song": song_model.serialize()
                }, 200            
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    @admin_required
    def delete(self, id):
        try:
            # Validate ID
            try:
                song_id = int(id)
                if song_id < 1:
                    return {"error": "Invalid song ID"}, 400
            except (ValueError, TypeError):
                return {"error": "Invalid song ID format"}, 400
            
            song = SongsServices().get_song_by_id(song_id)

            del_audio = CloudinaryService().delete_file_by_url(song.audio_url)
            del_pdf = CloudinaryService().delete_file_by_url(song.pdf_url)
            del_cover = CloudinaryService().delete_file_by_url(song.cover_url)

            deleted_song = SongsServices().delete_song(song_id)
            if deleted_song and del_audio and del_pdf and del_cover:
                return {"message": "success"}, 200
            else:
                return {"error": f"Fail to delete song (id: {song_id})"}, 400
        except Exception as err:
            return {"error": f"{err}"}, 400

class SearchResources(Resource):
    def get(self):
        params, error = validate_search_params(request.args)
        
        if error:
            return {"error": error}, 400
        
        # Extract sanitized parameters
        title = params['title']
        artist = params['artist']
        song_type = params['type']
        keyword = params['keyword']
        sort_by = params['sort_by']
        order = params['order']
        limit = params['limit']
        page = params['page']
        per_page = params['per_page']
        language = params['language']
        
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
            
            if language == 'zh-CN' and song.title_zhcn:
                song_data['display_title'] = song.title_zhcn
            elif language == 'zh-TW' and song.title_zhhk:
                song_data['display_title'] = song.title_zhhk
            else:
                song_data['display_title'] = song_data.get('title', '')
            
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
            # Validate ID
            try:
                song_id = int(id)
                if song_id < 1:
                    return {"error": "Invalid song ID"}, 400
            except (ValueError, TypeError):
                return {"error": "Invalid song ID format"}, 400
            
            count = SongsServices().add_play_count(song_id, 0)
            return {"playCount": count}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400
        
    def post(self, id):
        try:
            # Validate ID
            try:
                song_id = int(id)
                if song_id < 1:
                    return {"error": "Invalid song ID"}, 400
            except (ValueError, TypeError):
                return {"error": "Invalid song ID format"}, 400
            
            count = SongsServices().add_play_count(song_id, 1)
            return {"playCount": count}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400

    def delete(self, id):
        try:
            # Validate ID
            try:
                song_id = int(id)
                if song_id < 1:
                    return {"error": "Invalid song ID"}, 400
            except (ValueError, TypeError):
                return {"error": "Invalid song ID format"}, 400
            
            count = SongsServices().add_play_count(song_id, -1)
            return {"message": "success"}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400

class UploadAudioResource(Resource):
    @admin_required
    def post(self):
        try:
            audio_file = request.files.get('audio')
            title = sanitize_input(request.form.get('title'))
            artist = sanitize_input(request.form.get('artist'))
            
            if not audio_file:
                return {"error": "No audio file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            if not artist:
                return {"error": "Artist is required"}, 400
            
            # Validate title and artist length
            if len(title) > MAX_TITLE_LENGTH:
                return {"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH}"}, 400
            if len(artist) > MAX_ARTIST_LENGTH:
                return {"error": f"Artist exceeds maximum length of {MAX_ARTIST_LENGTH}"}, 400
            
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
            title = sanitize_input(request.form.get('title'))
            folder = sanitize_input(request.form.get('folder', 'covers'))
            
            if not image_file:
                return {"error": "No image file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            
            # Validate title length
            if len(title) > MAX_TITLE_LENGTH:
                return {"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH}"}, 400
            
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
            title = sanitize_input(request.form.get('title'))
            
            if not pdf_file:
                return {"error": "No PDF file provided"}, 400
            if not title:
                return {"error": "Title is required"}, 400
            
            # Validate title length
            if len(title) > MAX_TITLE_LENGTH:
                return {"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH}"}, 400
            
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