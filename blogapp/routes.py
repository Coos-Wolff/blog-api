from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from blogapp import service
from blogapp.exceptions import EmailAlreadyExistsError, InvalidCredentialsError, PostTitleAlreadyExistsError, \
    NotFoundError, ForbiddenError, UnauthorizedError
from blogapp.models import BlogPost

blog_bp = Blueprint("blog", __name__, url_prefix="/post")

@blog_bp.route("/")
def get_all_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    posts = service.get_all_posts(page, per_page)

    if not posts:
        return jsonify(error="No blog posts found"), 404
    return jsonify(posts), 200

@blog_bp.route("/<int:post_id>")
def show_post(post_id):
    post = service.get_post_by_id(post_id)
    if not post:
        return jsonify(error=f"No post found for [{post_id}]"), 404
    return jsonify(post), 200

@blog_bp.route("/add", methods=["POST"])
@jwt_required()
def add_post():
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error=create_missing_field_message("body")), 400

    required_fields = ["title", "subtitle", "date", "body", "img_url"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify(error=f"Missing required fields: {missing}"), 400

    blog_post = BlogPost(
        title=data["title"],
        subtitle=data["subtitle"],
        date=data["date"],
        body=data["body"],
        author_id=current_user_id,
        img_url=data["img_url"],
    )
    try:
        persisted_post = service.add_post(blog_post)
        return jsonify(persisted_post), 201
    except PostTitleAlreadyExistsError as error:
        return jsonify(error=str(error)), 409

@blog_bp.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    current_user_id = int(get_jwt_identity())
    try:
        service.delete_post(post_id, current_user_id)
        return jsonify(message=f"post with [{post_id}] is deleted"), 200
    except NotFoundError as error:
        return jsonify(error=str(error)), 404
    except ForbiddenError as error:
        return jsonify(error=str(error)), 403
    except UnauthorizedError as error:
        return jsonify(error=str(error)), 401

@blog_bp.route("/<int:post_id>", methods=["PATCH"])
@jwt_required()
def patch_post(post_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error=create_missing_field_message("body")), 400

    fields = {k: data[k] for k in ("title", "subtitle", "body") if k in data and data[k] is not None}
    if not fields:
        return jsonify(error="No patchable fields provided"), 400

    try:
        updated_post = service.update_post(post_id, current_user_id, fields)
        return jsonify(updated_post), 200
    except NotFoundError as error:
        return jsonify(error=str(error)), 404
    except ForbiddenError as error:
        return jsonify(error=str(error)), 403
    except UnauthorizedError as error:
        return jsonify(error=str(error)), 401
    except PostTitleAlreadyExistsError as error:
        return jsonify(error=str(error)), 409

@blog_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify(error=create_missing_field_message("body")), 400
    if not data.get("email"):
        return jsonify(error=create_missing_field_message("email")), 400
    if not data.get("name"):
        return jsonify(error=create_missing_field_message("name")), 400
    if not data.get("password"):
        return jsonify(error=create_missing_field_message("password")), 400

    try:
        registered_user = service.register_user(data)
        return jsonify(registered_user), 201
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except EmailAlreadyExistsError as error:
        return jsonify(error=str(error)), 409

@blog_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error=create_missing_field_message("body")), 400
    if not data.get("email"):
        return jsonify(error=create_missing_field_message("email")), 400
    if not data.get("password"):
        return jsonify(error=create_missing_field_message("password")), 400

    try:
        access_token = service.login(data)
        return jsonify(access_token=access_token), 200
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except InvalidCredentialsError:
        return jsonify(error="Invalid email or password"), 401

def register_routes(app):
    app.register_blueprint(blog_bp)

def create_missing_field_message(field):
    return f"Missing {field} in body"