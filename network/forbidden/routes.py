from forbidden import forbidden_blue
from Base import database
from flask import render_template


@forbidden_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@forbidden_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@forbidden_blue.route("/",methods=["GET","POST"])
def index():
    return render_template("forbidden_index.html")
