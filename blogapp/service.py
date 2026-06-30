from werkzeug.security import generate_password_hash

from blogapp import repository
from blogapp.exceptions import EmailAlreadyExistsError
from blogapp.models import User

def get_all_posts(page, per_page):
    posts =  repository.get_all_posts(page, per_page)
    if posts is None:
        return None
    return [post.to_dict() for post in posts]

def get_post_by_id(post_id):
    post =  repository.get_post_by_id(post_id)
    if post is None:
        return None
    return post.to_dict()

def add_post(blog_post):
    return repository.add_post(blog_post)

def update_post(post_id, fields):
    return repository.patch_post(post_id, fields)

def delete_post(post_id):
    return repository.delete_post(post_id)

def register_user(data):
    required_fields = ("email", "name", "password")
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    email = data.get("email")
    user = repository.find_user_by_email(email)
    if user:
        raise EmailAlreadyExistsError("Email already exists")

    hashed_password = generate_password_hash(data.get("password"))
    new_user = User(
        email=email,
        name=data.get("name"),
        password=hashed_password
    )
    registered_user = repository.add_user(new_user)
    return registered_user.to_dict()

