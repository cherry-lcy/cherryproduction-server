from flask import Flask
from extensions import db, cors, api, access_logger
from config import Config
from dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cors.init_app(app)
    access_logger.init_app(app)
    
    app.register_blueprint(dashboard_bp)
    
    from resources import register_routes
    register_routes(api)
    api.init_app(app)
    
    with app.app_context():
        from models.songs import SongsModel
        from models.tags import TagsModel
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)