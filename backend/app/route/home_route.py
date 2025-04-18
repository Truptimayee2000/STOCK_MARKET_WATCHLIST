from flask import request, jsonify
from datetime import datetime
from app import app
from dbconfig import db, mail
from flask_mail import Message
from models import User, OTPVerification, Stock, Watchlist, PreviousStockChange
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import threading, time, random



app.config['SECRET_KEY'] = "give your secret key"
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.route("/")
def index():
    return "Hello World"


#  Registration

@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email_id = data.get("email_id")
    password = data.get("password")

    if not email_id or not password:
        return jsonify({"error": "Email and password are required"})

    otp_code = str(random.randint(100000, 999999))

    existing_otp = OTPVerification.query.filter_by(email_id=email_id).first()
    if existing_otp:
        existing_otp.otp = otp_code
        existing_otp.created_on = datetime.now()
    else:
        new_otp = OTPVerification(email_id=email_id, otp=otp_code)
        db.session.add(new_otp)

    db.session.commit()

    try:
        msg = Message("Your OTP Code", sender=app.config["MAIL_USERNAME"], recipients=[email_id])
        msg.body = f"Your OTP is {otp_code}. It will expire in 5 minutes."
        mail.send(msg)
        return jsonify({"message": "OTP sent successfully"})
    except Exception as e:
        return jsonify({"error": f"Error sending email: {e}"})



# Verify OTP 
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email_id = data.get("email_id")
    otp = data.get("otp")
    password = data.get("password")

    if not email_id or not otp or not password:
        return jsonify({"error": "Email, OTP, and password are required"})

    otp_entry = OTPVerification.query.filter_by(email_id=email_id, otp=otp).first()
    if not otp_entry:
        return jsonify({"error": "Invalid OTP"})

    if (datetime.now() - otp_entry.created_on).total_seconds() > 300:
        return jsonify({"error": "OTP expired"})

    new_user = User(email_id=email_id, password=password)  
    db.session.add(new_user)
    db.session.delete(otp_entry)  
    db.session.commit()

    return jsonify({"message": "User registered successfully!"})


# User Login 
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email_id=data.get('email_id')).first()

    if not user or user.password != data.get('password'):
        return jsonify({"error": "Invalid email or password"})

    access_token = create_access_token(identity=user.user_id)

    return jsonify({"message": "Login Successfully", "access_token": access_token})

#  Get Stock 
@app.route("/stocks", methods=["GET"])
def get_all_stocks():
    stocks = Stock.query.all()

    if not stocks:
        return jsonify({"message": "No stocks found"})

    stock_data = [
        {
            "symbol": stock.symbol,
            "name": stock.name,
            "price": stock.price,
            "change": stock.change
        }
        for stock in stocks
    ]

    return jsonify(stock_data)


# Get Watchlist
@app.route("/watchlist", methods=["GET"])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()

    watchlist = (
        db.session.query(
            Watchlist.user_id,
            User.email_id,
            Watchlist.symbol,
            Stock.name,
            Stock.price,
            Stock.change
        )
        .join(User, User.user_id == Watchlist.user_id)
        .join(Stock, Stock.symbol == Watchlist.symbol)
        .filter(Watchlist.user_id == user_id)
        .all()
    )

    watchlist_data = []
    changes_detected = []  # To store symbols with a detected change
    user_email = None

    for w in watchlist:
        user_email = w.email_id  # Will be same for all since it's filtered by user
        prev = PreviousStockChange.query.filter_by(symbol=w.symbol).first()

        if prev:
            if w.change != prev.last_change:
                changes_detected.append({
                    "symbol": w.symbol,
                    "name": w.name,
                    "price": w.price,
                    "change": w.change
                })
                prev.last_change = w.change
        else:
            # First time storing
            prev = PreviousStockChange(symbol=w.symbol, last_change=w.change)
            db.session.add(prev)

        watchlist_data.append({
            "user_id": w.user_id,
            "email": w.email_id,
            "symbol": w.symbol,
            "name": w.name,
            "price": w.price,
            "change": w.change,
        })

    db.session.commit()

    if changes_detected:
        send_bulk_stock_change_email(user_email, changes_detected)

    return jsonify(watchlist_data)


def send_bulk_stock_change_email(email, changes):
    subject = "Stock Alert: Changes Detected"
    body = "Hi,\n\nHere are the stock updates in your watchlist:\n\n"

    for item in changes:
        body += (
            f"Symbol: {item['symbol']}\n"
            f"Name: {item['name']}\n"
            f"Price: ₹{item['price']}\n"
            f"Change: {item['change']}%\n\n"
        )

    body += "Visit your watchlist to see more details."

    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)



#  Add Stock 
@app.route('/watchlist/add', methods=['POST'])
@jwt_required() 
def add_to_watchlist():
    try:
        data = request.get_json()
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({"error": "Symbol is required"})
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User authentication required"})
        
        existing_stock = Watchlist.query.filter_by(user_id=user_id, symbol=symbol).first()
        if existing_stock:
            return jsonify({"error": "Stock already in watchlist"})
        
        new_stock = Watchlist(user_id=user_id, symbol=symbol)
        db.session.add(new_stock)
        db.session.commit()

        return jsonify({"message": "Stock added to watchlist"})

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route('/watchlist/remove', methods=['POST'])
@jwt_required()
def remove_stock_from_watchlist():
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({"msg": "Symbol is required."})
        
        stock_to_remove = Watchlist.query.filter_by(user_id=current_user_id, symbol=symbol).first()
        
        if stock_to_remove:
            db.session.delete(stock_to_remove)
            db.session.commit()
            return jsonify({"msg": f"Stock {symbol} removed from watchlist."})
        else:
            return jsonify({"msg": "Stock not found in watchlist."})
    except Exception as e:
        return jsonify({"msg": f"Error removing stock: {str(e)}"})
    

# Update Stock Prices 
def update_stock_prices():
    while True:
        time.sleep(5)  
        with app.app_context():
            stocks = Stock.query.all()
            for stock in stocks:
                stock.change = round(random.uniform(-5, 5), 2)
                stock.price = round(stock.price + stock.change, 2)
            db.session.commit()

            socketio.emit("price_update", [
                {"symbol": stock.symbol, "price": stock.price, "change": stock.change}
                for stock in stocks
            ])

threading.Thread(target=update_stock_prices, daemon=True).start()



