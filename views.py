from flask import Blueprint, render_template, request

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/RSI2', methods=['GET', 'POST'])
def RSI2():
    data = request.form
    next_page = ""
    if request.method == 'POST':
        stock_list = request.form.get('stock')
        next_page = "result.html"
    else:
        next_page = "RSI2.html"

    return render_template(next_page)

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"