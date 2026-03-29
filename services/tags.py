from sqlalchemy import select, asc
from extensions import db
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
    
    def get_distinct_tag(self):
        query = select(TagsModel.tag).distinct().order_by(asc(TagsModel.tag))
        return db.session.scalars(query).all()
    
    def add_tag(self, tag_model):
        existing_tags = self.get_tag_by_sid(tag_model.sid)
        if any(t.tag == tag_model.tag for t in existing_tags):
            raise Exception(
                f"For song {tag_model.sid}, tag '{tag_model.tag}' already exists."
            )
        
        db.session.add(tag_model)
        db.session.commit()
        return tag_model
    
    def delete_tag(self, id):
        tag = self.get_tag_by_id(id)
        if not tag:
            raise Exception(f"Tag (id: {id}) does not exist.")
        
        db.session.delete(tag)
        db.session.commit()
        return True
    
    def delete_tag_by_sid(self, sid):
        tags = self.get_tag_by_sid(sid)
        if not tags:
            raise Exception(f"Song (id: {sid}) does not have tag.")
        
        for tag in tags:
            self.delete_tag(tag.id)

        return True