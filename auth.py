from flask import Blueprint

user_bp = Blueprint('auth', __name__)

@user_bp.route('/auth/token')
def get_user(username):
    return f'Hello, {username}!'
