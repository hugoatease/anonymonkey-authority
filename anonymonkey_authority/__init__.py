from flask import Flask, g
from .schemas import db
from api import api
from redis import Redis


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
