from flask import Flask
from .config import Config
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recipeDB'

mysql = MySQL(app)



app.config.from_object(Config)
from app import views