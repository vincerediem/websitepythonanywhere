from flask import Blueprint, render_template, request, redirect, url_for
import sys
sys.path.append(r"C:\Users\kopen\OneDrive\Desktop\Code\Algo Trading\RSI\RSI 2")
import RSIv2_html as rsi2

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
    final_balance, initial_balance, stock, positions, trade_gains_losses, positions_sold = rsi2.backtest_strategy(stock)
    final_metrics = rsi2.return_final_metrics(final_balance, initial_balance, stock, positions, trade_gains_losses)
    return render_template("result.html", stock=stock, positions_sold=positions_sold, final_metrics=final_metrics)


@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"