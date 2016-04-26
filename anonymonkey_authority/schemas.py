from flask.ext.mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
    sub = db.StringField(required=True, primary_key=True)


class Survey(db.Document):
    survey_id = db.StringField(required=True, primary_key=True)
    owner = db.ReferenceField(User, required=True)
    recipients = db.ListField(db.StringField())
