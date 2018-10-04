from flask_restful import Resource, reqparse
from models import CustomerModel, RevokedTokenModel

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('email', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class CustomerRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        data = parser.parse_args()

        if CustomerModel.find_by_username(data['email']):
          return {'message': 'User {} already exists'. format(data['email'])}

        new_user = CustomerModel(
            email = data['email'],
            password = data['password']
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['email'])
            refresh_token = create_refresh_token(identity = data['email'])
            return {
                'message': 'Customer {} was created'.format( data['email']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500

class CustomerLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = CustomerModel.find_by_username(data['email'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['email'])}
        
        if data['password'] == current_user.password:
            access_token = create_access_token(identity = data['email'])
            refresh_token = create_refresh_token(identity = data['email'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}

class CustomerLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

class CustomerLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

#Only for testing purposes, TODO: Delete AllCustomers class
class AllCustomers(Resource):
    def get(self):
        return CustomerModel.return_all()
    
    def delete(self):
        return CustomerModel.delete_all()


class SecretResource(Resource):
    def get(self):
        return {
            "answer": 42
        }
