from flask import request, current_app, g
from flask_restful import abort
import jwt
import cryptography
from cryptography.hazmat.backends import default_backend
from functools import wraps
from anonymonkey_authority.schemas import User


def check_jwt():
    if 'Authorization' not in request.headers or request.headers['Authorization'][0:3] != 'JWT':
        print 'Missing authorization header'
        return False
    token = request.headers['Authorization'][4:]
    key = cryptography.hazmat.primitives.serialization.load_pem_public_key(current_app.config['OPENID_ISSUER_KEY'], backend=default_backend())
    try:
        claims = jwt.decode(token, key, audience=current_app.config['OPENID_CLIENT'], issuer=current_app.config['OPENID_ISSUER_CLAIM'])
        if claims is None:
            print 'Missing claims'
            return False
        g.id_token = claims
        return True
    except jwt.InvalidTokenError as ex:
        print 'Invalid token'
        print ex
        return False


def api_login(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if check_jwt():
            return func(*args, **kwargs)
        return abort(401)
    return decorated_view


def get_user():
    user = User.objects.with_id(g.id_token['sub'])
    if user is None:
        user = User(sub=g.id_token['sub'])
        user.save()
    return user
