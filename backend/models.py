from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from dbconfig import db, mail

#  User Table
class User(db.Model):
    __tablename__ = 'user_management'
    __table_args__ = {'schema': 'public'}  

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    is_active = db.Column(db.Boolean, default=True)

    def get_watchlist(self):
        return db.session.query(Stock).join(
            Watchlist, Watchlist.symbol == Stock.symbol
        ).filter(Watchlist.user_id == self.user_id).all()

  
#  OTP Verification Table
class OTPVerification(db.Model):
    __tablename__ = 'otp_verification'
    __table_args__ = {'schema': 'public'}

    otp_id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(255), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())


#  Stock Table
class Stock(db.Model):
    __tablename__ = 'stock'
    __table_args__ = {'schema': 'public'}

    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False, default=0.0)


# Watchlist Table 
class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    __table_args__ = {'schema': 'public'}

    watch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  
    symbol = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Watchlist {self.symbol}>"


#  Populate Stocks Function
def populate_stocks():
    existing_stocks = Stock.query.count()
    if existing_stocks == 0:
        initial_stocks = [
            Stock(symbol="AAPL", name="Apple Inc.", price=150.0, change=0.0),
            Stock(symbol="GOOGL", name="Alphabet Inc.", price=2800.0, change=0.0),
            Stock(symbol="TSLA", name="Tesla Inc.", price=700.0, change=0.0),
            Stock(symbol="MSFT", name="Microsoft Corp.", price=290.0, change=0.0),
        ]
        db.session.bulk_save_objects(initial_stocks)
        db.session.commit()

class PreviousStockChange(db.Model):
    __tablename__ = 'previous_stock_change'
    symbol = db.Column(db.String, primary_key=True)
    last_change = db.Column(db.Float)


with app.app_context():
    db.create_all()
    populate_stocks()
