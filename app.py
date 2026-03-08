# app.py
from flask import Flask
from extensions import db, cors, api
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cors.init_app(app)

    from resources import register_routes
    register_routes(api)  # must run before init_app so routes are registered
    api.init_app(app)
    
    with app.app_context():
        from models.songs import SongsModel
        from models.tags import TagsModel
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)