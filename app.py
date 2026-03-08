from flask import Flask
from extentions import db, cors, api
from config import Config
from resources import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cors.init_app(app)
    api.init_app(app)
    
    with app.app_context():
        db.create_all()

    register_routes(api)
    
    return app

app = create_app()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://root:Cherry5052005@localhost/Web_Ex"

if __name__ == '__main__':
    app.run(debug=True)