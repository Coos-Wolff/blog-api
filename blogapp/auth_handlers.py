from flask import jsonify
from blogapp.extensions import jwt

@jwt.unauthorized_loader
def handle_missing_token(reason):
    return jsonify(error="Authentication required"), 401

@jwt.invalid_token_loader
def handle_invalid_token(reason):
    return jsonify(error="Authentication required"), 401

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return jsonify(error="Authentication token has expired"), 401