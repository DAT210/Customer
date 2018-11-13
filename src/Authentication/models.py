from run import db
from run import pwd_context

class Customer(db.Model):
    __tablename__ = "customer_table"
    customer_id = db.Column(db.Integer, primary_key = True, nullable = False)
    customer_email = db.Column(db.String(128), unique = True, nullable = False)
    customer_password = db.Column(db.String(128), unique = False, nullable = True)

    first_name = db.Column(db.String(128), unique = False, nullable = True)
    last_name = db.Column(db.String(128), unique = False, nullable = True)
    customer_birthday = db.Column(db.Date, unique = False, nullable = True)
    customer_phone = db.Column(db.Integer, unique = False, nullable = True)
    address_id = db.Column(db.Integer, unique = True, nullable = True)

    @staticmethod
    def generate_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return pwd_context.verify(password, hash)

    @classmethod
    def find_by_cid(cls, cid):
        return cls.query.filter_by(customer_id = cid).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(customer_email = email).first()
    
    @classmethod
    def number_of_customers(cls):
        records = db.session.query(cls).all()
        number = len(records)
        return number

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # TODO: Remove this method before production!
    @classmethod
    def return_all(cls):
        def to_json(x):
            customer_address = None
            if x.address_id:
                customer_address = Address.find_by_address_id(x.address_id)
            
            if customer_address:
                return {
                'email': x.customer_email,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'password': x.customer_password,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'birthday': x.customer_birthday,
                'phone': x.customer_phone,
                'city': customer_address.city,
                'postcode': customer_address.postcode,
                'street_name': customer_address.street_name,
                'street_number': customer_address.street_number,
                'apartment_number': customer_address.apartment_number
                }

            return {
                'email': x.customer_email,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'password': x.customer_password,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'birthday': x.customer_birthday,
                'phone': x.customer_phone,
                'city': None,
                'postcode': None,
                'street_name': None,
                'street_number': None,
                'apartment_number': None
                }

        return {'customers': list(map(lambda x: to_json(x), Customer.query.all()))}

    # TODO: Remove this method before production!
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except Exception as err:
            return {'message': 'Something went wrong', "error": str(err)}


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(128))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


class Address(db.Model):
    __tablename__ = "customer_address"
    address_id = db.Column(db.Integer, primary_key = True, nullable = False)
    city = db.Column(db.String(128), unique = False, nullable = True)
    postcode = db.Column(db.SmallInteger, unique = False, nullable = True)
    street_name = db.Column(db.String(128), unique = False, nullable = True)
    street_number = db.Column(db.String(128), unique = False, nullable = True)
    apartment_number = db.Column(db.String(128), unique = False, nullable = True)
    
    @classmethod
    def find_by_address_id(cls, aid):
        return cls.query.filter_by(address_id = aid).first()
        
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()