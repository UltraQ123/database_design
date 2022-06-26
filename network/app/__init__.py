from flask import Flask
from Base.models import database
from user import user_blue
from card import card_blue
from cardBag import cardBag_blue
from cardSet import cardSet_blue
from forbidden import forbidden_blue
from api import  api_blue
from flask import render_template, flash, redirect, url_for, request

database.connect()
app = Flask(__name__,static_folder='static',template_folder="templates")
app.config["SECRET_KEY"] = 'b8a0e5e48f7e4577a020b8502dcb7fc8'
#随机生成的秘钥，防止报错"Must provide secret_key to use csrf"
app.config['JSON_AS_ASCII'] = False


app.register_blueprint(user_blue, url_prefix='/user')
app.register_blueprint(api_blue,url_prefix='/api')
app.register_blueprint(card_blue,url_prefix='/card')
app.register_blueprint(cardBag_blue,url_prefix='/cardBag')
app.register_blueprint(cardSet_blue,url_prefix='/cardSet')
app.register_blueprint(forbidden_blue,url_prefix='/forbidden')

from . import routes
