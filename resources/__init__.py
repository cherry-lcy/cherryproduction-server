from flask_restful import Api

from .admin import AdminResource
from .songs import SongsResources, SongResources, SearchResources
from .tags import TagsResources, TagResources, TagByIdResource

def register_routes(api):
    api.add_resource(AdminResource, "/api/admin")
    
    api.add_resource(SongsResources, "/api/songs")
    api.add_resource(SongResources, "/api/song/<int:id>")
    api.add_resource(SearchResources, "/api/songs/search")
            
    api.add_resource(TagsResources, "/api/tags")
    api.add_resource(TagResources, "/api/tags/<title>")
    api.add_resource(TagByIdResource, "/api/tag/<int:id>")