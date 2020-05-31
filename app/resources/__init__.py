from flask import Blueprint
from flask_restx import Api
from flask_jwt_extended import JWTManager



jwt = JWTManager()

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',#'X-API-KEY',
        'description':'Please input Access token'
    }
}

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/documentation', title='User management API', version='0.1', description='An API to manage user authentication/authorization', authorizations=authorizations, security='apikey')


api.add_namespace(signup)
api.add_namespace(login)
api.add_namespace(logout)
api.add_namespace(roles)
api.add_namespace(manage_user)
api.add_namespace(update_user)
api.add_namespace(password_manager)

