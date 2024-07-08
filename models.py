from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()



class UserDetails(db.Model, UserMixin):
    __tablename__ = 'user_details'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    @property
    def is_active(self):
        # You can add more logic here if needed
        return True

    @property
    def is_authenticated(self):
        # All logged-in users are authenticated
        return True

    @property
    def is_anonymous(self):
        # False for regular users
        return False

    def get_id(self):
        return str(self.user_id)

class StoreUser(db.Model):
    __tablename__ = 'store_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(20), nullable=False)
    @property
    def is_active(self):
        # You can add more logic here if needed
        return True

    @property
    def is_authenticated(self):
        # All logged-in users are authenticated
        return True

    @property
    def is_anonymous(self):
        # False for regular users
        return False

    def get_id(self):
        return str(self.id)

class Products(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    __tablename__ = 'purchase'
    purchase_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False)
    email_id = db.Column(db.String(200), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    date_of_purchase = db.Column(db.Date, nullable=False)
