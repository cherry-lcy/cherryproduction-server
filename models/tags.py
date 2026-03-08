from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from extensions import db

class TagsModel(db.Model):
    __tablename__ = "Tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    sid: Mapped[int] = mapped_column(ForeignKey('Songs.id'), nullable=False)
    
    song = relationship("SongsModel", backref="tags")

    def serialize(self):
        return {
            "id": self.id,
            "tag": self.tag,
            "song_id": self.sid
        }