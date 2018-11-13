from flask_restful import Resource, reqparse
from models import Customer, RevokedTokenModel, Address
import random
import json

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

registration_parser = reqparse.RequestParser()
registration_parser.add_argument('email', help = 'This field cannot be blank', required = True)
registration_parser.add_argument('password', help = 'This field cannot be blank', required = True)
registration_parser.add_argument('first_name', help = 'This field can be blank', required = False)
registration_parser.add_argument('last_name', help = 'This field can be blank', required = False)
registration_parser.add_argument('birthday', help = 'This field can be blank', required = False)
registration_parser.add_argument('phone', help = 'This field can be blank', required = False)
registration_parser.add_argument('city', help = 'This field can be blank', required = False)
registration_parser.add_argument('postcode', help = 'This field can be blank', required = False)
registration_parser.add_argument('street_name', help = 'This field can be blank', required = False)
registration_parser.add_argument('street_number', help = 'This field can be blank', required = False)
registration_parser.add_argument('apartment_number', help = 'This field can be blank', required = False)

# Registration
## URI: /registration
class CustomerRegistration(Resource):
    def post(self):
        data = registration_parser.parse_args()

        if not data["email"]:
            return {'message': 'Email is required'}

        if not data["password"]:
            return {'message': 'Password is required'}

        # Checking if the email is already in our database, returns message if it is. Countinues if not.
        if Customer.find_by_email(data['email']):
            return {'message': 'User {} already exists'. format(data['email'])}

        # Hashing password as soon as possible, Please dont add anything between the line above and below this comment
        data["password"] = Customer.generate_hash(data["password"])

        #TODO: Improve this \/
        cid = random.randint(10000000, 99999999)
        while Customer.find_by_cid(cid):
            if cid >= 99999999:
                cid = 10000000
            else:
                cid += 1

        aid = None
        if data["city"] or data["postcode"] or data["street_name"] or data["street_number"] or data["apartment_number"]:
            aid = random.randint(10000000, 99999999)
            while Address.find_by_address_id(aid):
                if aid >= 99999999:
                    aid = 10000000
                else:
                    aid += 1
        
        # Making a new model with the email and password provided
        new_customer = Customer(
            customer_id = cid,
            customer_email = data["email"],
            customer_password = data["password"],
            first_name = data["first_name"],
            last_name = data["last_name"],
            customer_birthday = data["birthday"],
            customer_phone = data["phone"],
            address_id = aid
        )

        if aid:
            new_address = Address(
            address_id = aid,
            city = data["city"],
            postcode = data["postcode"],
            street_name = data["street_name"],
            street_number = data["street_number"],
            apartment_number = data["apartment_number"]
        )

        try:
            # Saving the new user to the database. the method is located in models.py
            new_customer.save_to_db()
            new_address.save_to_db()

            # Making tokens so the customer is logged in
            access_token = create_access_token(identity = cid)
            refresh_token = create_refresh_token(identity = cid)

            return {
                'message': 'Customer {} was created'.format( data['email']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201
        except Exception as err:
            return {'message': 'Something went wrong', 
                "error": str(err)
                }, 500

# Login
## URI: /login
class CustomerLogin(Resource):
    def post(self):
        data = registration_parser.parse_args()

        # Finding customer from the database
        current_customer = Customer.find_by_email(data['email'])
        if not current_customer:
            return {'message': 'User {} doesn\'t exist'.format(data['email'])}
        
        # Checking password, if correct, it makes tokens to log the customer in
        if Customer.verify_hash(data["password"], current_customer.customer_password):
            access_token = create_access_token(identity = current_customer.customer_id)
            refresh_token = create_refresh_token(identity = current_customer.customer_id)
            return {
                'message': 'Logged in as {}'.format(current_customer.customer_email),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 202
        else:
            return {'message': 'Wrong email or password'}, 401

#Logout access
## URI: /logout/access
class CustomerLogoutAccess(Resource):
    # Requires a jwt object to run, which basically means that the customer must be logged in to log out(which makes sense)
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}, 200
        except Exception as err:
            return {'message': 'Something went wrong', 
                "error": str(err)
                }, 500

# Logout refresh
## URI: /logout/refresh
class CustomerLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}, 200
        except Exception as err:
            return {'message': 'Something went wrong', 
                "error": str(err)
                }, 500

# Refresh access token with refresh token
## URI: /token/refresh
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}, 201



#Only for testing purposes
## TODO: (IMPORTANTE) Delete "AllCustomers" class before production!
class AllCustomers(Resource):
    def get(self):
        return Customer.return_all(), 200
    
    def delete(self):
        print("Got into delete")
        return Customer.delete_all(), 200


# The following classes are for the Api
## URI: /v1/customer/cid
class GetCid(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object == None:
                return {"message": "Invalid cid. The customer doesnt exist in our database"}, 401

            return {"message": "The cid was found", 
                "cid": current_customer
                }, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500

## URI: /v1/customer/email
class GetEmail(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object == None:
                return {"message": "Invalid cid. The customer doesnt exist in our database"}, 401
            
            return {"message": "Email of the customer was found", "email": customer_object.customer_email}, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500

## URI: /v1/customer/birthday
class GetBirthday(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object.customer_id == None:
                return {"message": "Invalid cid. The customer doesn't exist in our database"}, 401
            
            return {"message": "Birthday of the customer was found", "birthday": customer_object.customer_birthday}, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500

## URI: /v1/customer/phone
class GetPhone(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object.customer_id == None:
                return {"message": "Invalid cid. The customer doesn't exist in our database"}, 401
            
            return {"message": "Phone of the customer was found", "phone": customer_object.customer_phone}, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500

## URI: /v1/customer/name
class GetName(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object == None:
                return {"message": "Invalid cid. The customer doesnt exist in our database"}, 401

            return {"message": "Name of the customer was found", 
                "first_name": customer_object.first_name, 
                "last_name": customer_object.last_name
                }, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500

## URI: /v1/customer/address
class GetAddress(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object.customer_id == None:
                return {"message": "Invalid cid. The customer doesn't exist in our database"}, 401

            if customer_object.address_id == None:
                return {"message": "The customer has no address"}, 401

            customer_address = Address.find_by_address_id(customer_object.address_id)

            return {"message": "Address of the customer was found", 
                "city": customer_address.city,
                "postcode": customer_address.postcode,
                "street_name": customer_address.street_name,
                "street_number": customer_address.street_number,
                "apartment_number": customer_address.apartment_number
                }, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500
                
## URI: /v1/customer/all
class GetAll(Resource):
    @jwt_required
    def get(self):
        try:
            # Getting the cid from the jwt.
            current_customer = get_jwt_identity()

            # Getting the customer from the database through the model in models.py
            customer_object = Customer.find_by_cid(current_customer)

            # Checks if no object got returned in the query, then return 401 Unauthorized.
            if customer_object.customer_id == None:
                return {"message": "Invalid cid. The customer doesn't exist in our database"}, 401

            if customer_object.address_id:
                

                customer_address = Address.find_by_address_id(customer_object.address_id)

                return {"message": "Customer was found", 
                    "cid": current_customer,
                    "email": customer_object.customer_email,
                    "first_name": customer_object.first_name, 
                    "last_name": customer_object.last_name,
                    "birthday": customer_object.customer_birthday,
                    "phone": customer_object.customer_phone,
                    "city": customer_address.city,
                    "postcode": customer_address.postcode,
                    "street_name": customer_address.street_name,
                    "street_number": customer_address.street_number,
                    "apartment_number": customer_address.apartment_number
                    }, 202
                
            return {"message": "Customer was found", 
                "cid": current_customer,
                "email": customer_object.customer_email,
                "first_name": customer_object.first_name, 
                "last_name": customer_object.last_name,
                "birthday": customer_object.customer_birthday,
                "phone": customer_object.customer_phone,
                "city": None,
                "postcode": None,
                "street_name": None,
                "street_number": None,
                "apartment_number": None
                }, 202

        except Exception as err:
            return {"message": "Something went wrong on the server", 
                "error": str(err)
                }, 500