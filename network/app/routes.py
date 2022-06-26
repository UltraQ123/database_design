#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
###主要是注册登录管理
from app import app
from Base import database
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from Base.models import User #模型

from flask_login import LoginManager
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(name):  #login时传入
    try:
        user = User.get(User.name == name)  # 查
    except:
        user = None
    return user


@app.before_request
def before_request():
    if database.is_closed():
        database.connect()


@app.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def rootindex():
    return redirect(url_for('index'))  # 重定向


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/forget', methods=['GET'])
def forget():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('forget.html')


@app.route('/login', methods=['GET'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('password_login.html')