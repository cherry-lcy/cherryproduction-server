from sqlalchemy import select, asc
from extentions import db
from models.tags import TagsModel

class TagsServices():
    def get_all_tag(self):
        query = select(TagsModel).order_by(asc(TagsModel.sid))
        return db.session.scalars(query).all()
    
    def get_tag_by_id(self, id):
        return db.session.get(TagsModel, id)
    
    def get_tag_by_sid(self, sid):
        query = select(TagsModel).where(TagsModel.sid == sid)
        return db.session.scalars(query).all()
    
    def add_tag(self, tag_model):
        tag = self.get_tag_by_sid(tag_model.sid)
        if tag.tag == tag_model.tag:
            raise Exception(f"For song {tag_model.id}, tag {tag_model.tag} already exists.")
        
        db.session.add(tag_model)
        db.session.commit()
        return tag_model
    
    def delete_tag(self, id):
        tag = self.get_tag_by_id(id)
        if not tag:
            raise Exception(f"Tag (id: {id}) does not exist.")
        
        db.session.delete(id)
        db.session.commit()
        return True
    
    def delete_tag_by_sid(self, sid):
        tags = self.get_tag_by_sid(sid)
        if not tags:
            raise Exception(f"Song (id: {sid}) does not have tag.")
        
        for tag in tags:
            self.delete_tag(tag.id)

        return True