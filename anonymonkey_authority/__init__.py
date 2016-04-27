from flask import Flask, g, render_template, jsonify
from .schemas import db
from api import api
from redis import Redis
import json


app = Flask(__name__)
app.config.from_object('settings')
app.config['MONGODB_SETTINGS'] = {
    'host': app.config['MONGODB_HOST'],
    'port': app.config['MONGODB_PORT'],
    'db': app.config['MONGODB_DB'],
    'tz_aware': True
}

redis = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

@app.before_request
def before_request():
    g.redis = redis

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

db.init_app(app)
api.init_app(app)


@app.route('/survey_access/<token>')
def survey_access(token):
    return render_template('survey_access.html', params=json.dumps({
        'token': token
    }))


@app.route('/.well-known/anonymonkey-authority')
def discovery_endpoint():
    return jsonify({
        'token_key': {
            'pem': {
                'public': app.config['TOKEN_KEY_PUBLIC']
            }
        }
    })