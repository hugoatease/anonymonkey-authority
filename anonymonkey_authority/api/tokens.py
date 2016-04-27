from flask import current_app, g
from flask_restful import Resource, reqparse, abort
from anonymonkey_authority.schemas import TokenBlacklist, Survey
from uuid import uuid4
import jwt
from hashlib import sha256


def decode_token(token):
    return jwt.decode(token, key=current_app.config['TOKEN_KEY_PUBLIC'], algorithms='RS256',
                      issuer=current_app.config['TOKEN_ISSUER'], audience=current_app.config['TOKEN_ISSUER'])


def check_token(token):
    try:
        token = decode_token(token)
    except jwt.InvalidTokenError:
        return False

    if TokenBlacklist.objects(survey=Survey.objects.with_id(token['survey_id']), jtid=token['jtid']).first() is None:
        return True
    return False


class TokenInitializeResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('survey_token', type=unicode, required=True)
        args = parser.parse_args()

        if not check_token(args['survey_token']):
            return abort(401)

        token = decode_token(args['survey_token'])

        c = str(uuid4())
        g.redis.set('anonymonkey.c.' + token['survey_id'] + '.' + token['jtid'], c)

        h = sha256(c).hexdigest()
        return {'h': h}


class TokenAuthorizeResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('survey_token', type=unicode, required=True)
        parser.add_argument('value', type=unicode, required=True)
        args = parser.parse_args()

        if not check_token(args['survey_token']):
            return abort(401)

        token = decode_token(args['survey_token'])
        c = g.redis.get('anonymonkey.c.' + token['survey_id'] + '.' + token['jtid'])
        g.redis.delete('anonymonkey.c.' + token['survey_id'] + '.' + token['jtid'])

        survey = Survey.objects.with_id(token['survey_id'])

        anonymous_token = jwt.encode({
            'iss': current_app.config['TOKEN_ISSUER'],
            'aud': survey.base_url,
            'token': sha256(c + args['value']).hexdigest(),
            'survey_id': token['survey_id']
        }, current_app.config['TOKEN_KEY'], algorithm='RS256')

        print anonymous_token

        blacklist = TokenBlacklist(
            survey=Survey.objects.with_id(token['survey_id']),
            jtid=token['jtid']
        )

        blacklist.save()

        return {
            'token': anonymous_token,
            'c': c
        }
