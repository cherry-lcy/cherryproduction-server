from flask_restful import Api

from .admin import AdminResource
from .songs import SongsResources, SongResources, SearchResources, LikeResources, UploadAudioResource, UploadImageResource, UploadPdfResource
from .tags import TagsResources, TagResources, TagByIdResource
from .artist import ArtistsResource
from .type import TypesResource
from .title import TitlesResource, TitlesByArtistResource
from .upload import UploadResource

def register_routes(api):
    api.add_resource(AdminResource, "/api/admin")
    
    api.add_resource(SongsResources, "/api/songs")
    api.add_resource(SongResources, "/api/song/<int:id>")
    api.add_resource(SearchResources, "/api/songs/search")
    api.add_resource(UploadAudioResource, "/api/upload-audio")
    api.add_resource(UploadImageResource, "/api/upload-image")
    api.add_resource(UploadPdfResource, "/api/upload-pdf")
            
    api.add_resource(TagsResources, "/api/tags")
    api.add_resource(TagResources, "/api/tags/<title>")
    api.add_resource(TagByIdResource, "/api/tag/<int:id>")
    
    api.add_resource(ArtistsResource, "/api/artists")
    
    api.add_resource(TitlesResource, "/api/titles")
    api.add_resource(TitlesByArtistResource, "/api/titles/<artist>")

    api.add_resource(TypesResource, "/api/types")

    api.add_resource(LikeResources, "/api/like/<int:id>")

    api.add_resource(UploadResource, "/api/upload-signature")