from flask import current_app, render_template, url_for, jsonify, g
from flask_restful import Resource, reqparse, marshal_with, abort
from anonymonkey_authority.schemas import Survey
from .auth import api_login, get_user
from .fields import survey_fields
import jwt
import uuid
import requests


def fetch_surveyor_key(base_url):
    cached = g.redis.get('anonymonkey.surveyors.public_key.' + base_url)
    if cached is None:
        discovery = requests.get(base_url + '/.well-known/anonymonkey').json()
        g.redis.set('anonymonkey.surveyors.public_key.' + base_url, discovery['key']['pem']['public'])
        g.redis.expire('anonymonkey.surveyors.public_key.' + base_url, 1800)
        return discovery['key']['pem']['public']
    else:
        return cached


class SurveyListResource(Resource):
    @api_login
    @marshal_with(survey_fields)
    def get(self):
        return list(Survey.objects(owner=get_user()))

    @api_login
    @marshal_with(survey_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('register_token', type=unicode, required=True)
        args = parser.parse_args()

        base_url = jwt.decode(args['register_token'], verify=False)['iss']

        data = jwt.decode(
            args['register_token'],
            fetch_surveyor_key(base_url),
            issuer=base_url,
            algorithm='RS256'
        )

        survey = Survey(
            survey_id=data['survey_id'],
            name=data['survey_name'],
            base_url=data['iss'],
            owner=get_user()
        )
        survey.save()
        return survey


class SurveyResource(Resource):
    @marshal_with(survey_fields)
    def get(self, survey_id):
        return Survey.objects.with_id(survey_id)


class SurveyShareResource(Resource):
    @api_login
    def post(self, survey_id):
        survey = Survey.objects.with_id(survey_id)
        if survey.owner.sub != get_user().sub:
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=unicode, required=True)
        args = parser.parse_args()

        survey.update(push__recipients=args['email'])

        token = jwt.encode({
            'iss': current_app.config['TOKEN_ISSUER'],
            'aud': current_app.config['TOKEN_ISSUER'],
            'jtid': str(uuid.uuid4()),
            'survey_id': str(survey.id)
        }, current_app.config['TOKEN_KEY'], algorithm='RS256')

        url = url_for('survey_access', token=token, _external=True)
        html = render_template('email.html', survey_name=survey.name, url=url)

        req = requests.post('https://api.mailgun.net/v3/' + current_app.config['MAILGUN_DOMAIN'] + '/messages', data={
            'from': current_app.config['MAIL_SENDER'],
            'to': args['email'],
            'subject': survey.name + ' survey invitation',
            'html': html,
            }, auth=('api', current_app.config['MAILGUN_KEY']))

        print req.content

        return jsonify({'error': False, 'email': args['email']})
