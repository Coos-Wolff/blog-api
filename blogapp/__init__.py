import os

from flask import Flask
from dotenv import load_dotenv
from blogapp.models import db, BlogPost, User

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from blogapp.routes import register_routes
    register_routes(app)

    return app