import os
from app import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from flask_mail import Mail

POSTGRES_URL="localhost"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="Trupti"
POSTGRES_DB="stock_market_watchlist"
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PASSWORD,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI']=DB_URL
app.config['SQLALCHEMY_Track_MODIFICATION']=False
app.config['SQLALCHEMY_ENGINE_OPTIONS']={'poolclass':NullPool}
db=  SQLAlchemy(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False  
app.config["MAIL_USERNAME"] = "samaltruptimayee4@gmail.com"
app.config["MAIL_PASSWORD"] = "qncz hncp hqgw ulww"
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
mail = Mail(app)

    
   

