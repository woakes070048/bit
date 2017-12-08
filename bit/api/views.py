# flask
from flask import Blueprint
from flask import jsonify

# flask_restplus
from flask_restplus import Resource, Api

# superset
from superset import app
from superset import csrf
from superset import db

from bit.models.analytics import Identify

print('api init')

blueprint_api = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    blueprint_api,
    title='BIT <- SEGMENT API',
    version='1.0',
    doc='/doc/',
    description='A sample API'
)
app.register_blueprint(blueprint_api)

csrf.exempt(blueprint_api)


@api.route('/v1/batch')
class IdentifyResource(Resource):
    def get(self):
        return jsonify(
            users=[i.to_json() for i in db.session.query(Identify).all()]
        )

    def post(self):

        batch = api.payload.get('batch', {})
        # print(batch)
        obj = Identify()
        obj.email = 'dasdsad@dasdas.com'

        db.session.merge(obj)
        db.session.commit()

        return jsonify(
            users=[i.to_json() for i in db.session.query(Identify).all()])

# @api.route('/my-resource/<id>', endpoint='my-resource')
# @api.doc(params={'id': 'An ID'})
# class MyResource(Resource):
#     def get(self, id):
#         return {}
#
#     @api.doc(responses={403: 'Not Authorized'})
#     def post(self, id):
#         api.abort(403)
