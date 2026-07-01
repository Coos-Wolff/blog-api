from sqlalchemy import select
from .models import db, BlogPost, User

def get_all_posts(page, per_page):
    # TODO Order_by should be by date but data is a string not a DateTime object, we should refactor this.
    return db.paginate(
        db.select(BlogPost).order_by(BlogPost.id),
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_post_by_id(post_id):
    return db.session.execute(select(BlogPost).where(BlogPost.id == post_id)).scalar()

def find_post_by_title(title: str):
    return db.session.execute(select(BlogPost).where(BlogPost.title == title)).scalar()

def add_post(blog_post):
    try:
        db.session.add(blog_post)
        db.session.commit()
        return blog_post
    except Exception as ex:
        db.session.rollback()
        raise ex

def patch_post(post_id, fields):
    post = get_post_by_id(post_id)
    if post is None:
        return None
    try:
        for key, value in fields.items():
            setattr(post, key, value)
        db.session.commit()
        return post
    except Exception as ex:
        db.session.rollback()
        raise ex

def delete_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return False
    try:
        db.session.delete(post)
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        raise ex

def find_user_by_email(email: str):
    return db.session.execute(select(User).where(User.email == email)).scalar()

def add_user(user: User):
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as ex:
        db.session.rollback()
        raise ex
