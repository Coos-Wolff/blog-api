from flask import Blueprint, request, jsonify
from blogapp import service
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
def add_post():
    data = request.get_json(silent=True)

    if not data:
        return jsonify(error="Missing JSON body"), 400

    required_fields = ["title", "subtitle", "data", "body", "author", "img_url"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify(error=f"Missing required fields: {missing}"), 400

    blog_post = BlogPost(
        title=data["title"],
        subtitle=data["subtitle"],
        date=data["date"],
        body=data["body"],
        author=data["author"],
        img_url=data["img_url"]
    )
    persisted_post = service.add_post(blog_post)
    return jsonify(persisted_post.to_dict()), 201

@blog_bp.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    is_deleted = service.delete_post(post_id)
    if is_deleted:
        return jsonify(message=f"post with [{post_id}] is deleted"), 200
    return jsonify(error=f"Could not find post with id: [{post_id}]"), 404

@blog_bp.route("/update", methods=["PATCH"])
def patch_post():
    data = request.get_json(silent=True)
    if not data or "id" not in data:
        return jsonify(error="Missing JSON body and/or post id."), 400

    fields = {k: data[k] for k in ("title", "subtitle", "body") if k in data and data[k] is not None}
    if not fields:
        return jsonify(error="No patchable fields provided"), 400

    updated_post = service.update_post(data["id"], fields)
    if not updated_post:
        return jsonify(error=f"No post found for [{data['id']}]"), 404
    return jsonify(updated_post.to_dict()), 200

def register_routes(app):
    app.register_blueprint(blog_bp)
