from flask import Blueprint, render_template, request, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/RSI2', methods=['GET', 'POST'])
def RSI2():
    if request.method == 'POST': #if a stock is entered, will take you to results page
        stock_list = request.form.get('stock')
        return redirect(url_for('views.RSI2_result', stock=stock_list))
    else: #else reruns page
        return render_template('RSI2.html')

@views.route('/RSI2/<stock>')
def RSI2_result(stock):
    # Perform any additional operations based on the stock value if needed

    return render_template("result.html", stock=stock)

'''@views.route('/RSI2', methods=['GET', 'POST'])
def result():'''

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"