from flask import current_app, render_template, url_for, jsonify
from flask_restful import Resource, reqparse, marshal_with, abort
from anonymonkey_authority.schemas import Survey
from .auth import api_login, get_user
from .fields import survey_fields
import jwt
import arrow
import requests


class SurveyListResource(Resource):
    @api_login
    @marshal_with(survey_fields)
    def get(self):
        return list(Survey.objects(owner=get_user()))

    @api_login
    @marshal_with(survey_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('survey_id', type=unicode, required=True)
        args = parser.parse_args()

        survey = Survey(
            survey_id=args['survey_id'],
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
            'iat': arrow.utcnow().datetime,
            'survey_id': str(survey.id)
        }, current_app.config['SECRET_KEY'])

        #url = url_for('index_all', path='/survey/' + str(survey.id), _external=True) + '?token=' + token
        url = 'http://localhost:8000/survey/' + str(survey.id) + '/?token=' + token
        html = render_template('email.html', survey_name='COUCOU', url=url)

        req = requests.post('https://api.mailgun.net/v3/' + current_app.config['MAILGUN_DOMAIN'] + '/messages', data={
            'from': current_app.config['MAIL_SENDER'],
            'to': args['email'],
            'subject': 'COUCOU' + ' survey invitation',
            'html': html,
            }, auth=('api', current_app.config['MAILGUN_KEY']))

        print req.content

        return jsonify({'error': False, 'email': args['email']})
