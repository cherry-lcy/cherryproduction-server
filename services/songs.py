from sqlalchemy import select, asc, desc, and_
from models.songs import SongsModel
from extensions import db
from services.tags import TagsServices

class SongsServices():
    def get_song_by_id(self, id):
        return db.session.get(SongsModel, id)
    
    def get_all_songs(self):
        query = select(SongsModel).order_by(asc(SongsModel.release_date))
        return db.session.scalars(query).all()
    
    def get_song_by_title(self, title):
        query = select(SongsModel).where(SongsModel.title == title)
        return db.session.scalar(query)
    
    def get_songs_by_artist(self, artist):
        query = select(SongsModel).where(SongsModel.artist == artist)
        return db.session.scalars(query).all()
    
    def get_songs_by_type(self, type):
        query = select(SongsModel).where(SongsModel.type == type)
        return db.session.scalars(query).all()
    
    def get_songs_by_title_and_artist(self, title, artist):
        query = select(SongsModel).where(
            and_(SongsModel.title == title, SongsModel.artist == artist)
        )
        return db.session.scalar(query)
        
    def get_ordered_songs(self, col_name, order):
        col = getattr(SongsModel, col_name)
        order_func = asc if order == "asc" else desc
        query = select(SongsModel).order_by(order_func(col))
        return db.session.scalars(query).all()
    
    def get_all_artist(self):
        query = select(SongsModel.artist).distinct().order_by(asc(SongsModel.artist))
        return db.session.scalars(query).all()
    
    def get_all_title(self, artist=None):
        if artist:
            query = select(SongsModel.title).distinct().where(SongsModel.artist == artist).order_by(asc(SongsModel.title))
        else:
            query = select(SongsModel.title).distinct().order_by(asc(SongsModel.title))

        return db.session.scalars(query).all()
    
    def add_song(self, song_model):
        existing = self.get_songs_by_title_and_artist(
            song_model.title, song_model.artist
        )
        if existing:
            raise Exception(
                f"Song '{song_model.title}' by {song_model.artist} already exists."
            )
        
        db.session.add(song_model)
        db.session.commit()
        return song_model

    def add_play_count(self, id):
        song = self.get_song_by_id(id)
        if not song:
            raise Exception(f"Song (id: {id}) is not found.")
        
        song.play_count += 1
        db.session.commit()
        return song.play_count
    
    def update_song(self, song_model):
        song = self.get_song_by_id(song_model.id)
        if not song:
            raise Exception(f"Song id {song_model.id} not found.")
        
        song.title = song_model.title if song_model.title else song.title
        song.artist = song_model.artist if song_model.artist else song.artist
        song.type = song_model.type if song_model.type else song.type
        song.release_date = song_model.release_date if song_model.release_date else song.release_date
        song.audio_url = song_model.audio_url if song_model.audio_url else song.audio_url
        song.video_url = song_model.video_url if song_model.video_url else song.video_url
        song.pdf_url = song_model.pdf_url if song_model.pdf_url else song.pdf_url
        song.cover_url = song_model.cover_url if song_model.cover_url else song.cover_url
        
        db.session.commit()
        return song
        
    def delete_song(self, id):
        song = self.get_song_by_id(id) 
        if not song:
            raise Exception(f"Song (id: {id}) is not found.")
        
        try:
            tags_service = TagsServices()
            tags_service.delete_tag_by_sid(id)
        except Exception as e:
            print(f"Warning when deleting tags: {e}")
        
        db.session.delete(song)
        db.session.commit()
        return True