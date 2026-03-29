from flask_restful import Resource
from flask import request
from services.tags import TagsServices

class TypesResource(Resource):
    def get(self):
        types = TagsServices().get_distinct_tag()
        
        return {
            'types': types
        }, 200