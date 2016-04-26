from flask_restful import Api
from .survey import SurveyListResource, SurveyResource, SurveyShareResource
from .tokens import TokenInitializeResource, TokenAuthorizeResource


api = Api()
api.add_resource(SurveyListResource, '/api/surveys')
api.add_resource(SurveyResource, '/api/surveys/<survey_id>')
api.add_resource(SurveyShareResource, '/api/surveys/<survey_id>/share')
api.add_resource(TokenInitializeResource, '/api/tokens/initialize')
api.add_resource(TokenAuthorizeResource, '/api/tokens/authorize')
