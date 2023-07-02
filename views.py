from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/RSI2')
def RSI2():
    return "<h1>RSI2</h1>"

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"