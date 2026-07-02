import sys
import traceback
import os
import logging
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=== Starting Flask app ===")

try:
    from flask import Flask, jsonify
    from extensions import db, cors, api, access_logger
    from config import Config
    from dashboard import dashboard_bp
    logger.info("Imports successful")
except Exception as e:
    logger.error(f"Import failed: {e}")
    traceback.print_exc()
    raise

def create_app():
    logger.info("Creating app...")
    app = Flask(__name__)
    app.config.from_object(Config)
    
    logger.info(f"FLASK_ENV: {app.config.get('FLASK_ENV')}")
    # Mask database URL for security (only show first/last chars)
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_url:
        masked_url = db_url[:30] + "..." + db_url[-20:] if len(db_url) > 50 else db_url
        logger.info(f"DATABASE_URL: {masked_url}")
    
    try:
        db.init_app(app)
        cors.init_app(app)
        access_logger.init_app(app)
        logger.info("Extensions initialized")
    except Exception as e:
        logger.error(f"Extension init failed: {e}")
        traceback.print_exc()
        raise
    
    # Register blueprint
    app.register_blueprint(dashboard_bp)
    logger.info("Dashboard blueprint registered")
    
    # Register RESTful routes
    from resources import register_routes
    register_routes(api)
    api.init_app(app)
    logger.info("RESTful routes registered")
    
    # Create tables
    try:
        with app.app_context():
            # Import models inside app context to avoid circular imports
            from models.songs import SongsModel
            from models.tags import TagsModel
            db.create_all()
            logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")
        traceback.print_exc()

    
    logger.info("App created successfully")
    return app

app = create_app()

# Health check endpoints (must be registered after app creation)
@app.route('/')
@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "ok",
        "message": "Flask is running",
        "database_connected": _check_database()
    })

def _check_database():
    """Check if database is accessible"""
    try:
        from extensions import db
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Root endpoint with more info
@app.route('/info')
def info():
    return jsonify({
        "name": "Cherry Production API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/", "/health", "/info", "/songs", "/api/..."]
    })

# if __name__ == "__main__":
#     app.run()