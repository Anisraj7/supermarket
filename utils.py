from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from models import db, Purchase
import json
from decimal import Decimal
from flask import jsonify 

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

mail = Mail()

def fetch_sales_data(start_date, end_date):
    purchases = db.session.query(
        Purchase.item,
        db.func.sum(Purchase.quantity).label('total_quantity'),
        db.func.sum(Purchase.quantity * Purchase.rate).label('total_amount')
    ).filter(
        Purchase.date_of_purchase.between(start_date, end_date)
    ).group_by(Purchase.item).all()
    
    def decimal_to_float(d):
        return float(d) if isinstance(d, Decimal) else d
    
    # Create a dictionary to hold sales data
    sales_data = {
        purchase.item: {
            'QTY': decimal_to_float(purchase.total_quantity),
            'Amount': decimal_to_float(purchase.total_amount)
        }
        for purchase in purchases
    }
    return sales_data


def send_sales_report(email, subject, sales_data):
    msg = Message(subject=subject, sender='anisraj103@gmail.com', recipients=[email])
    msg.body = json.dumps(sales_data, indent=6)
    
    mail.send(msg)
    print("Sales report sent to", email)
    

def daily_sales_report(app):
    try:
        with app.app_context():
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            sales_data = fetch_sales_data(yesterday, today)
            send_sales_report('anisraj0706@gmail.com', 'Daily Sales Report', sales_data)
    except Exception as e:
        print(f"Error in daily_sales_report: {e}")

def weekly_sales_report(app):
    try:
        with app.app_context():
            today = datetime.now().date()
            last_week = today - timedelta(days=7)
            sales_data = fetch_sales_data(last_week, today)
            send_sales_report('anisraj0706@gmail.com', 'Weekly Sales Report', sales_data)
    except Exception as e:
        print(f"Error in weekly_sales_report: {e}")


def immediate_sales_report(email):
    today = datetime.now().date()
    sales_data = fetch_sales_data("2024-07-01", today)
    send_sales_report(email, 'Immediate Sales Report', sales_data)
    print(sales_data)

