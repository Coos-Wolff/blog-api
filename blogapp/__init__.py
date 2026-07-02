import os

from flask import Flask
from dotenv import load_dotenv
from blogapp.models import BlogPost, User
from blogapp.extensions import jwt, db

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    jwt.init_app(app)
    db.init_app(app)

    from blogapp import auth_handlers

    with app.app_context():
        db.create_all()

    from blogapp.routes import register_routes
    register_routes(app)

    return app