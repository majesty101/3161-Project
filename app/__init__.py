from flask import Flask
from .config import Config
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recipedb'

mysql = MySQL(app)

UPLOAD_FOLDER = 'uploads/'





app.config.from_object(Config)
from app import views
