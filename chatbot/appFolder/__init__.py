from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

application = app = Flask(__name__)
app.config['SECRET_KEY'] = '3590242450687c7350814c30fc3f0f2b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#app.config['SERVER_NAME'] = '127.0.0.1:5000'
db = SQLAlchemy(app)
CORS(app)
login_mangager = LoginManager(app)
login_mangager.login_view = 'login'


from appFolder import  routes
