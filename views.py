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
        stock_list = stock_list.split()
        return redirect(url_for('views.RSI2_result', stock_list=','.join(stock_list)))
    else: #else reruns page
        return render_template('RSI2.html')

@views.route('/RSI2/<stock_list>')
def RSI2_result(stock_list):
    stock_list = stock_list.split(',')
    final_balance, initial_balance, stock, positions, trade_gains_losses, positions_sold = rsi2.backtest_strategy(stock_list)
    final_metrics = rsi2.return_final_metrics(final_balance, initial_balance, stock, positions, trade_gains_losses)
    trade_metrics, df = rsi2.trade_metrics(stock, positions_sold) #gives list of dics for each trade and df to print
    return render_template("result.html", 
                           stock_list=stock_list, 
                           positions_sold=positions_sold, 
                           final_metrics=final_metrics,
                           trade_metrics=trade_metrics,
                           df=df.to_html())

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"