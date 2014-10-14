from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from settings import settings

app = Flask(__name__)
app.config.update(settings)
db = SQLAlchemy(app)
app.url_dict = {}

#from model import *
