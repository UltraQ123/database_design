from user import user_blue
from Base import database
from flask_login import current_user
from flask import redirect, render_template,url_for
@user_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@user_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@user_blue.route("/space",methods=["GET","POST"])
def space():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("user_space.html")

@user_blue.route("/my_set",methods=["GET","POST"])
def my_set():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("user_setlist.html")