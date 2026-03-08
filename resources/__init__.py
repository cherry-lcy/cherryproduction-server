from .songs import SongsResources, SongResources, SearchResources
from .tags import TagResources, TagByIdResource

def register_routes(api):
    api.add_resource(SongsResources, "/songs")
    api.add_resource(SongResources, "/song/<int:id>")
    api.add_resource(SearchResources, "/songs/search")
            
    api.add_resource(TagResources, "/api/tag/<str:title>")
    api.add_resource(TagByIdResource, "/api/tag/<int:id>")