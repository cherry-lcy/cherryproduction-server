from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from extensions import db

class SongsModel(db.Model):
    __tablename__ = "Songs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, 
        server_default=func.now()
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_zhcn: Mapped[str] = mapped_column(String(200), nullable=True)
    title_zhhk: Mapped[str] = mapped_column(String(200), nullable=True)
    artist: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    release_date: Mapped[datetime] = mapped_column(nullable=False)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    pdf_url: Mapped[str] = mapped_column(String(500), nullable=False)
    play_count: Mapped[int] = mapped_column(
        BigInteger, 
        nullable=False, 
        default=0,
        server_default='0'
    )
    cover_url: Mapped[str] = mapped_column(String(500), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "title_zhcn": self.title_zhcn,
            "title_zhhk": self.title_zhhk,
            "artist": self.artist,
            "type": self.type,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "audio_url": self.audio_url,
            "video_url": self.video_url,
            "pdf_url": self.pdf_url,
            "play_count": self.play_count,
            "cover_url": self.cover_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }