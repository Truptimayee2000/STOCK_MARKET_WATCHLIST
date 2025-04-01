from flask import request, jsonify
from datetime import datetime
from app import app
from dbconfig import db, mail
from flask_mail import Message
from models import User, OTPVerification, Stock, Watchlist, PriceAlert
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import threading, time, random

app.config['SECRET_KEY'] = "Trupti123"
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ==========================
# 📌 Index Route
# ==========================
@app.route("/")
def index():
    return "Hello World"

# ==========================
# 📌 Register & Send OTP
# ==========================
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email_id = data.get("email_id")
    password = data.get("password")

    if not email_id or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # ✅ Generate a 6-digit OTP
    otp_code = str(random.randint(100000, 999999))

    # ✅ Store OTP in the database
    existing_otp = OTPVerification.query.filter_by(email_id=email_id).first()
    if existing_otp:
        existing_otp.otp = otp_code
        existing_otp.created_on = datetime.now()
    else:
        new_otp = OTPVerification(email_id=email_id, otp=otp_code)
        db.session.add(new_otp)

    db.session.commit()

    # ✅ Send OTP via Email
    try:
        msg = Message("Your OTP Code", sender=app.config["MAIL_USERNAME"], recipients=[email_id])
        msg.body = f"Your OTP is {otp_code}. It will expire in 5 minutes."
        mail.send(msg)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Error sending email: {e}"}), 500

# ==========================
# 📌 Verify OTP & Register User
# ==========================
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email_id = data.get("email_id")
    otp = data.get("otp")
    password = data.get("password")

    if not email_id or not otp or not password:
        return jsonify({"error": "Email, OTP, and password are required"}), 400

    # ✅ Validate OTP from database
    otp_entry = OTPVerification.query.filter_by(email_id=email_id, otp=otp).first()
    if not otp_entry:
        return jsonify({"error": "Invalid OTP"}), 400

    # ✅ Check OTP expiration (5 minutes)
    if (datetime.now() - otp_entry.created_on).total_seconds() > 300:
        return jsonify({"error": "OTP expired"}), 400

    # ✅ Register user
    new_user = User(email_id=email_id, password=password)  # 🔴 Store **hashed password** instead
    db.session.add(new_user)
    db.session.delete(otp_entry)  # Remove OTP after verification
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 200

# ==========================
# 📌 User Login API (Returns JWT Token)
# ==========================
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email_id')
    password = data.get('password')

    user = User.query.filter_by(email_id=email).first()

    if not user or user.password != password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # ✅ Generate JWT Token
    access_token = create_access_token(identity=user.user_id)

    # 🔹 Get User Watchlist
    watchlist = Watchlist.query.filter_by(user_id=user.user_id).all()
    if watchlist:
        # 🔹 Check Price Alerts for Stocks in the Watchlist
        for watch_item in watchlist:
            stock = Stock.query.filter_by(symbol=watch_item.symbol).first()
            if stock:
                # Get the PriceAlert for this stock and user
                price_alert = PriceAlert.query.filter_by(user_id=user.user_id, symbol=watch_item.symbol).first()
                if price_alert:
                    # Check if the price has crossed the alert threshold
                    if (price_alert.alert_type == 'above' and stock.price >= price_alert.threshold_price) or \
                       (price_alert.alert_type == 'below' and stock.price <= price_alert.threshold_price):
                        send_price_alert_email(price_alert, stock.price)  # Send price alert email
    
    return jsonify({"message": "Login Successfully", "access_token": access_token}), 200

def send_price_alert_email(alert, current_price):
    """Sends an email alert when a stock price crosses the alert threshold."""
    try:
        user = User.query.filter_by(id=alert.user_id).first()  # Retrieve the user
        if user:
            # Prepare the email message
            msg = Message(
                subject=f"📈 Price Alert: {alert.symbol}",
                sender=app.config["MAIL_USERNAME"],  # Sender email
                recipients=[user.email_id],  # Recipient email
                body=(
                    f"🚀 The price of {alert.symbol} has {alert.alert_type} your alert price of {alert.threshold_price}.\n\n"
                    f"Updated Price: {current_price}\n\n"
                    f"🔗 Check your portfolio for more details!"
                )
            )
            mail.send(msg)  # Send email
            print(f"✅ Email sent to {user.email_id} for {alert.symbol}")

    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")  # Log any errors



# ==========================
# 📌 Get Stock by Symbol
# ==========================
@app.route("/stocks", methods=["GET"])
def get_all_stocks():
    stocks = Stock.query.all()

    if not stocks:
        return jsonify({"message": "No stocks found"}), 404

    stock_data = [
        {
            "symbol": stock.symbol,
            "name": stock.name,
            "price": stock.price,
            "change": stock.change
        }
        for stock in stocks
    ]

    return jsonify(stock_data), 200


# ==========================
# 📌 Get Watchlist (Using Manual Join)
# ==========================
@app.route("/watchlist", methods=["GET"])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()

    # ✅ Manual join between Watchlist, User, and Stock
    watchlist = (
        db.session.query(
            Watchlist.user_id,
            User.email_id,  
            Watchlist.symbol,
            Stock.name,
            Stock.price,
            Stock.change
        )
        .join(User, User.user_id == Watchlist.user_id)  # ✅ Correct join on user_id
        .join(Stock, Stock.symbol == Watchlist.symbol)  # ✅ Join on stock symbol
        .filter(Watchlist.user_id == user_id)  # ✅ Filter by logged-in user
        .all()
    )

    # ✅ Convert the result to JSON format
    watchlist_data = [
        {
            "user_id": w.user_id,
            "email": w.email_id,
            "symbol": w.symbol,
            "name": w.name,
            "price": w.price,
            "change": w.change,
        }
        for w in watchlist
    ]

    return jsonify(watchlist_data), 200

# ==========================
# 📌 Add Stock to Watchlist
# ==========================
@app.route('/watchlist/add', methods=['POST'])
@jwt_required()  # Ensures that the user is authenticated
def add_to_watchlist():
    try:
        data = request.get_json()
        symbol = data.get('symbol')

        # Validate the symbol input
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
        
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User authentication required"}), 401
        
        # Check if symbol already exists for the user
        existing_stock = Watchlist.query.filter_by(user_id=user_id, symbol=symbol).first()
        if existing_stock:
            return jsonify({"error": "Stock already in watchlist"}), 400
        
        # Add the stock to the user's watchlist
        new_stock = Watchlist(user_id=user_id, symbol=symbol)
        db.session.add(new_stock)
        db.session.commit()

        return jsonify({"message": "Stock added to watchlist"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/watchlist/remove', methods=['POST'])
@jwt_required()
def remove_stock_from_watchlist():
    try:
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get the symbol from the request JSON
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({"msg": "Symbol is required."}), 400
        
        # Query the watchlist to find the stock for the current user
        stock_to_remove = Watchlist.query.filter_by(user_id=current_user_id, symbol=symbol).first()
        
        if stock_to_remove:
            db.session.delete(stock_to_remove)
            db.session.commit()
            return jsonify({"msg": f"Stock {symbol} removed from watchlist."}), 200
        else:
            return jsonify({"msg": "Stock not found in watchlist."}), 404
    except Exception as e:
        return jsonify({"msg": f"Error removing stock: {str(e)}"}), 500
    

# ==========================
# 📌 Update Stock Prices (Background Thread)
# ==========================
def update_stock_prices():
    while True:
        time.sleep(5)  # ✅ Simulate real-time price updates every 5 seconds
        with app.app_context():
            stocks = Stock.query.all()
            for stock in stocks:
                stock.change = round(random.uniform(-5, 5), 2)
                stock.price = round(stock.price + stock.change, 2)
            db.session.commit()

            # ✅ Emit price updates to WebSocket clients
            socketio.emit("price_update", [
                {"symbol": stock.symbol, "price": stock.price, "change": stock.change}
                for stock in stocks
            ])

# ✅ Start background thread for stock updates
threading.Thread(target=update_stock_prices, daemon=True).start()



