from flask import Blueprint, render_template, request, redirect, url_for
import RSIv2_html as rsi2
import RSIv2_html_complex as rsi2_complex

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

    #intial backtest
    final_balance, initial_balance, stock, positions, trade_gains_losses, positions_sold, closed_df, open_df, percent_gains_losses, fig, stock_prices, final_metrics = rsi2.backtest_strategy(stock_list)

    #converts plotly "fig" to html
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template("result.html", 
                           stock_list=stock_list, 
                           positions=positions, 
                           final_metrics=final_metrics,
                           closed_df=closed_df.to_html(),
                           open_df=open_df.to_html(),
                           plot_html=plot_html)

@views.route('/RSI2_complex', methods=['GET', 'POST'])
def RSI2_complex():
    if request.method == 'POST':
        stock_list = request.form.get('stock')
        stock_list = stock_list.split()

        rsi_period = int(request.form['rsi_period'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        initial_balance = float(request.form['initial_balance'])
        buy_rsi = request.form['buy_rsi']
        sell_rsi = request.form['sell_rsi']

        # Call the backtest_strategy function with form data
        final_balance, _, _, positions, _, _, closed_df, open_df, _, fig, _, final_metrics = rsi2_complex.backtest_strategy(stock_list, rsi_period, start_date, end_date, initial_balance, buy_rsi, sell_rsi)

        # Convert Plotly "fig" to HTML
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        return render_template("result.html", 
                               stock_list=stock_list, 
                               positions=positions, 
                               final_metrics=final_metrics,
                               closed_df=closed_df.to_html(),
                               open_df=open_df.to_html(),
                               plot_html=plot_html)
    else:
        # Render the form directly in the template
        return render_template('RSI2_complex.html')

@views.route('/SMA')
def SMA():
    return "<h1>SMA</h1>"