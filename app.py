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
        # Don't raise - let the app start even if DB has issues
        # Tables might already exist
    
    logger.info("App created successfully")
    return app

# Create app instance
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

# app.py - Add this new route for dynamic sitemap generation

@app.route('/sitemap.xml')
def generate_sitemap():
    """
    Dynamically generate sitemap.xml from database
    This endpoint is served from the backend but will be proxied by Cloudflare
    """
    from models.songs import SongsModel
    from datetime import date
    import time
    
    # Base URL for your frontend (Cloudflare Pages)
    # You can also read this from environment variable
    base_url = os.environ.get('FRONTEND_URL', 'https://www.cherryproduction.cc')
    
    # Start building XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # ========== STATIC PAGES ==========
    # Pages that don't change frequently
    static_pages = [
        ('/', 'daily', '1.0'),
        ('/search', 'daily', '0.9'),
        ('/privacy', 'yearly', '0.3'),
    ]
    
    current_date = date.today().isoformat()
    
    for path, changefreq, priority in static_pages:
        xml += f"""
  <url>
    <loc>{base_url}{path}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
    
    # ========== DYNAMIC PAGES (Songs) ==========
    # Fetch all songs from database
    try:
        songs = SongsModel.query.all()
        
        for song in songs:
            # Determine last modified date
            # Use release_date if available, otherwise created_at
            if song.release_date:
                lastmod = song.release_date.strftime('%Y-%m-%d')
            elif song.created_at:
                lastmod = song.created_at.strftime('%Y-%m-%d')
            else:
                lastmod = current_date
            
            # Generate URL for each song detail page
            song_url = f"{base_url}/detail?id={song.id}"
            
            xml += f"""
  <url>
    <loc>{song_url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
        
        app.logger.info(f"Generated sitemap with {len(songs)} songs")
        
    except Exception as e:
        # Log error but still return sitemap with static pages
        app.logger.error(f"Error generating dynamic sitemap: {e}")
    
    # Close the urlset tag
    xml += '\n</urlset>'
    
    # Return as XML response with proper caching headers
    from flask import Response
    response = Response(xml, mimetype='application/xml')
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response