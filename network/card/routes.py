from card import card_blue
from Base import database
from flask_login import current_user
from flask import redirect, render_template,url_for


@card_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@card_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@card_blue.route("/search",methods=["GET","POST"])
def index():
    return render_template("card_search.html")

@card_blue.route("/data/<int:card_id>/",methods=["GET","POST"])
def data(card_id:int):
    return render_template("card_data.html")