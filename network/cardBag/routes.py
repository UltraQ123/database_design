from cardBag import cardBag_blue
from Base import database
from flask_login import current_user
from flask import redirect, render_template,url_for


@cardBag_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@cardBag_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@cardBag_blue.route("/search/",methods=["GET","POST"])
def index():
    return render_template("cardBag_search.html")

@cardBag_blue.route("/data/<int:cardbag_id>/",methods=["GET","POST"])
def data(cardbag_id:int):
    return render_template("cardBag_data.html")