from blogapp import repository

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