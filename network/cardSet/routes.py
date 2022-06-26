from cardSet import cardSet_blue
from Base import database
from flask_login import current_user
from flask import redirect, render_template,url_for


@cardSet_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@cardSet_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@cardSet_blue.route("/search",methods=["GET","POST"])
def index():
    return render_template("cardSet_search.html")

@cardSet_blue.route("/data/<string:user>/<string:name>/",methods=["GET","POST"])
def data(user:str,name:str):
    return render_template("cardSet_data.html")