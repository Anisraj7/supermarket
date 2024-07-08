from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from models import db, UserDetails, StoreUser, Products, Purchase
from utils import hash_password, check_password, mail, daily_sales_report, weekly_sales_report, immediate_sales_report
from datetime import datetime, timedelta
import os
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from config import *
from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://root:anisraj@localhost/supermarket')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'flashkey'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'anisraj103@gmail.com'
app.config['MAIL_PASSWORD'] = 'sykbalbauigbzatd'

mail = Mail(app)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'userlogin'

@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))
def load_user(id):
    return StoreUser.query.get(int(id))

scheduler = BackgroundScheduler()  # <-- Initialize BackgroundScheduler
scheduler.start()  # <-- Start scheduler

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        hashed_password = hash_password(data['password'])
        new_user = UserDetails(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            sex=data['sex'],
            contact_number=data['contact_number'],
            email_id=data['email_id'],
            password=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('userlogin'))
        except:
            db.session.rollback()
            flash("User already exists", "error")
                    
    return render_template('signup_user.html')

@app.route('/store_user', methods=['GET', 'POST'])
def storeuser():
    if request.method == 'POST':
        data = request.form
        hashed_password = hash_password(data['password'])
        store_user = StoreUser(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            sex=data['sex'],
            contact_number=data['contact_number'],
            email_id=data['email_id'],
            password=hashed_password,
            designation=data['designation']
        )
        try:
            db.session.add(store_user)
            db.session.commit()
            flash("User added successfully", "success")
        except:
            db.session.rollback()
            flash("user already exists", "error")
        return render_template('admin_login.html')
    return render_template('store_user.html')

@app.route('/user_login', methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        data = request.form
        user = UserDetails.query.filter_by(email_id=data['email_id']).first()
        if user and check_password(user.password, data['password']):
            login_user(user)
            session['mail'] = data['email_id']
            return redirect(url_for('purchase'))
        else:
            flash("Invalid credentials", "error")

    return render_template('user_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logout success")
    return render_template('home.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        data = request.form
        user = StoreUser.query.filter_by(email_id=data['email_id']).first()
        if user and check_password(user.password, data['password']):
            login_user(user)
            flash("Login successful", "success")
            # return redirect(url_for('manage_items'))
            return render_template('admin_dashboard.html')
        else:
            flash("Invalid credentials", "error")
            
        return render_template('store_user.html')

    return render_template('admin_login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if current_user.is_authenticated:
        return render_template('admin_dashboard.html')

@app.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
    if request.method == 'POST':
        try:
            data = request.form
            mail = session.get('mail')
            user = UserDetails.query.filter_by(email_id=mail).first()
            if user:
                new_purchase = Purchase(
                    user_id=user.user_id,
                    email_id=mail,
                    item=data['item'],
                    quantity=data['quantity'],
                    rate=data['rate'],
                    date_of_purchase=datetime.strptime(data['date_of_purchase'], '%Y-%m-%d')
                )
                db.session.add(new_purchase)
                db.session.commit()
                flash("Purchase recorded successfully", "success")
            else:
                flash("User not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "error")
    
    mail = session.get('mail')
    return render_template('purchase.html', mail=mail)

@app.route('/purchase_details', methods=['GET'])
@login_required
def purchase_details():
    user = UserDetails.query.filter_by(email_id=session.get('mail')).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for('userlogin'))
    
    purchases = Purchase.query.filter_by(user_id=user.user_id).all()
    return render_template('purchase_details.html', purchases=purchases)

@app.route('/manage-items', methods=['GET', 'POST'])
def manage_items():
    if request.method == 'POST':
        data = request.form
        if data['action'] == 'add':
            existing_item = Products.query.filter_by(product_name=data['product_name']).first()
            if existing_item:
                flash(f"Product '{data['product_name']}' already exists. Please choose a different name.", 'error')
            else:
                new_item = Products(
                    product_name=data['product_name'],
                    rate=data['rate'],
                    stock=data['stock']
                )
                db.session.add(new_item)
                db.session.commit()
                flash("Item added successfully", 'success')
        elif data['action'] == 'delete':
            product_name = data['product_name']
            item = Products.query.filter_by(product_name=product_name).first()
            if item:
                db.session.delete(item)
                flash("Item deleted successfully")
            else:
                flash("Item not found")
        elif data['action'] == 'update':
            product_name = data['product_name']
            new_rate = data['rate']
            new_stock = int(data['stock'])
            item = Products.query.filter_by(product_name=product_name).first()
            if item:
                item.rate = new_rate
                item.stock += new_stock
                db.session.commit()
                flash("Item details updated successfully")
            else:
                flash("Item not found")
        db.session.commit()
        return redirect(url_for('manage_items'))
    
    products = Products.query.all()
    return render_template('manage_items.html', products=products)

@app.route('/total_items', methods=['GET', 'POST'])
def total_items():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required parameters.'}), 400

        try:
            # Check if dates are in valid format (YYYY-MM-DD)
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')

            # Query purchases within date range
            purchases = Purchase.query.filter(
                Purchase.date_of_purchase.between(start_date, end_date)
            ).all()

            # Calculate total items
            total_items = sum([purchase.quantity for purchase in purchases])

            return render_template('total_items.html', total_items=total_items)

        except ValueError as e:
            print(f"Error parsing dates: {e}")
            return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD format for dates.'}), 400

        except Exception as e:
            print(f"Error fetching total items: {e}")
            return jsonify({'error': 'Error fetching total items. Please check date format and try again.'}), 400
    else:
        return render_template('total_items.html')

@app.route('/high_spenders', methods=['GET', 'POST'])
def high_spenders():
    if request.method == 'POST' or request.args.get('json'):
        high_spenders = db.session.query(
            UserDetails.first_name, UserDetails.last_name,
            db.func.sum(Purchase.rate * Purchase.quantity).label('total_amount')
        ).join(Purchase).group_by(UserDetails.user_id).having(
            db.func.sum(Purchase.rate * Purchase.quantity) > 1000
        ).all()
        
        result = [{'name': f'{spender.first_name} {spender.last_name}', 'total_amount': spender.total_amount} for spender in high_spenders]
        
        if request.method == 'POST':
            return render_template('high_spenders.html', high_spenders=result)
        else:
            return jsonify(result)
    else:
        return render_template('high_spenders.html')

@app.route('/shampoo_sales', methods=['GET', 'POST'])
def shampoo_sales():
    shampoo_sales = None
    if request.method == 'POST' or request.args.get('json'):
        last_week = datetime.now() - timedelta(days=7)
        shampoo_sales = db.session.query(
            db.func.sum(Purchase.rate * Purchase.quantity)
        ).filter(
            Purchase.item == 'Shampoo',
            Purchase.date_of_purchase >= last_week
        ).scalar()
        
        if request.method == 'POST':
            return render_template('shampoo_sales.html', shampoo_sales=shampoo_sales)
        else:
            return jsonify({'shampoo_sales': shampoo_sales})
    else:
        return render_template('shampoo_sales.html')

@app.route('/send_immediate_report', methods=['POST'])  # <-- New route for sending email immediately
def send_immediate_report_route():
    email = request.form.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    try:
        immediate_sales_report(email)
        return jsonify({'message': 'Report sent successfully'}), 200
    except Exception as e:
        return jsonify({'exception': str(e)}), 500

scheduler = BackgroundScheduler()

# Schedule daily sales report
scheduler.add_job(
    func=daily_sales_report,
    trigger='cron',
    hour=11, minute=1,  # Adjust to the desired hour for daily report (e.g., 10 PM)
    args=[app],
)

# Schedule weekly sales report
scheduler.add_job(
    func=weekly_sales_report,
    trigger='cron',
    day_of_week='mon',
    hour=22, minute=1, # Adjust to the desired hour for weekly report (e.g., 11 AM)
    args=[app],
)

# Start the scheduler
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)