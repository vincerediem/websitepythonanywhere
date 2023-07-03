from flask import Blueprint, render_template, request

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/RSI2', methods=['GET', 'POST'])
def RSI2():
    data = request.form
    if request.method == 'POST': #if a stock is entered, will take you to results page
        stock_list = request.form.get('stock')
        return render_template('result.html')
    else: #else reruns page
        return render_template('RSI2.html')


'''@views.route('/RSI2', methods=['GET', 'POST'])
def result():'''

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"