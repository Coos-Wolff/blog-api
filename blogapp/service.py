from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from blogapp import repository
from blogapp.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from blogapp.models import User

DUMMY_HASH = generate_password_hash("Very.Long.Dummy.Hash.14903!")

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
    return repository.add_post(blog_post).to_dict()

def update_post(post_id, fields):
    return repository.patch_post(post_id, fields)

def delete_post(post_id):
    return repository.delete_post(post_id)

def register_user(data):
    missing = check_for_missing_fields(data, "email", "name", "password")
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

def login(data):
    missing = check_for_missing_fields(data,"email", "password")
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    user = repository.find_user_by_email(data.get("email"))
    if user is None:
        _ = check_password_hash(DUMMY_HASH, "1.3.Wrong.password.31.")
        raise InvalidCredentialsError("User not found")
    is_valid = check_password_hash(user.password, data.get("password"))
    if not is_valid:
        raise InvalidCredentialsError("Invalid login attempt")
    return create_access_token(str(user.id))


def check_for_missing_fields(data, *args):
    required_fields = args
    return [field for field in required_fields if not data.get(field)]