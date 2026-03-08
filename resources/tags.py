from flask_restful import Resource
from flask import request
from services.songs import SongsServices
from services.tags import TagsServices
from models.tags import TagsModel

class TagsResources(Resource):
    def get(self):
        tags = TagsServices().get_all_tag()
        return {
            "tags": [tag.serialize() for tag in tags]
        }, 200

class TagResources(Resource):
    def get(self, title):
        song = SongsServices().get_song_by_title(title)
        if not song:
            return {"error": f"Song {title} is not found."}
        tags = TagsServices().get_tag_by_title(title)
        return {
            "tags": [tag.serialize() for tag in tags]
        }
    def post(self, title):
        try:
            song = SongsServices().get_song_by_title(title)
            if not song:
                return {"error": f"Song {title} is not found."}
            new_tag = request.json
            if new_tag:
                new_tag_label = new_tag.get("tag")

                tag_model = TagsModel(tag=new_tag_label)
                tag_model = TagsServices().add_tag(tag_model)

                return {
                    "tag": tag_model.serialize()
                }, 200
        except Exception as err:
            return {"error": f"{err}"}
    def delete(self, title):
        try:
            song = SongsServices().get_song_by_title(title)
            if not song:
                return {"error": f"Song {title} is not found."}
            
            deleted_tags = TagsServices().delete_tag_by_sid(song.id)
            if deleted_tags:
                return {"message":"success"}, 200
            else:
                return {"error": f"Fail to delete tag for song {title}"}, 400
        except Exception as err:
            return {"error": f"{err}"}, 400
        
class TagByIdResource(Resource):
    def get(self, id):
        tag = TagsServices().get_tag_by_id(id)
        if tag:
            return {"tag": tag.serialize()}, 200
        else:
            return {"error": f"Tag (id: {id}) is not found."}, 404
    def delete(self, id):
        try: 
            tag = TagsServices().delete_tag(id)
            return {"message":"success"}, 200
        except Exception as err:
            return {"error": f"{err}"}, 400
