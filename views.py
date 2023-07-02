from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/RSI2')
def RSI2():
    return render_template("RSI2.html")

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"