from flask_restful import fields

user_fields = {
    'sub': fields.String
}

survey_fields = {
    'survey_id': fields.String,
    'owner': fields.Nested(user_fields),
    'recipients': fields.List(fields.String)
}
