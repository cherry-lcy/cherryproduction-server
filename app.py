import sys
import traceback

print("=== Starting Flask app ===")

try:
    from flask import Flask
    from extensions import db, cors, api, access_logger
    from config import Config
    from dashboard import dashboard_bp
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
    traceback.print_exc()
    raise

def create_app():
    print("Creating app...")
    app = Flask(__name__)
    app.config.from_object(Config)
    
    print(f"FLASK_ENV: {app.config.get('FLASK_ENV')}")
    print(f"DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    try:
        db.init_app(app)
        cors.init_app(app)
        access_logger.init_app(app)
        print("Extensions initialized")
    except Exception as e:
        print(f"Extension init failed: {e}")
        traceback.print_exc()
    
    app.register_blueprint(dashboard_bp)
    
    from resources import register_routes
    register_routes(api)
    api.init_app(app)
    
    # with app.app_context():
    #     from models.songs import SongsModel
    #     from models.tags import TagsModel
    #     db.create_all()
    
    print("App created successfully")
    return app

app = create_app()

@app.route('/')
@app.route('/health')
def health():
    return {"status": "ok", "message": "Flask is running"}

if __name__ == '__main__':
    app.run(debug=True)