from flask import Blueprint, render_template, request, redirect, url_for
from strategies import RSIv2_html as rsi2
from strategies import RSIv2_html_complex as rsi2_complex
from strategies import SMAv2 as sma2
from strategies import SMAv2_complex as sma2_complex
from strategies import overview as ov

views = Blueprint('views', __name__)

@views.route('/')
def home():
    index_list = ["SPY", "QQQ", "DIA"]
    stock_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "V", "NVDA", "META", "UNH", "LLY", "JPM", "XOM", "JNJ", "PG"]

    market_plot = ov.plot_last_year_prices(index_list)
    market_df = ov.create_stock_dataframe(stock_list)

    return render_template("home.html",
                           market_plot=market_plot,
                           market_df=market_df.to_html(index=False))

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


@views.route('/SMA', methods=['GET', 'POST'])
def SMA():
    if request.method == 'POST': #if a stock is entered, will take you to results page
        stock_list = request.form.get('stock')
        stock_list = stock_list.split()
        return redirect(url_for('views.SMA_result', stock_list=','.join(stock_list)))
    else: #else reruns page
        return render_template('SMA2.html')

@views.route('/SMA/<stock_list>')
def SMA_result(stock_list):
    stock_list = stock_list.split(',')

    #intial backtest
    _, _, _, positions, _, _, closed_df, open_df, _, fig, _, final_metrics = sma2.backtest_strategy(stock_list)

    #converts plotly "fig" to html
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template("result.html", 
                           stock_list=stock_list, 
                           positions=positions, 
                           final_metrics=final_metrics,
                           closed_df=closed_df.to_html(),
                           open_df=open_df.to_html(),
                           plot_html=plot_html)

@views.route('/SMA_complex', methods=['GET', 'POST'])
def SMA_complex():
    if request.method == 'POST':
        stock_list = request.form.get('stock')
        stock_list = stock_list.split()

        sma_period = int(request.form['sma_period'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        initial_balance = float(request.form['initial_balance'])
        buy_sma = request.form['buy_sma']
        sell_sma = request.form['sell_sma']

        # Call the backtest_strategy function with form data
        _, _, _, positions, _, _, closed_df, open_df, _, fig, _, final_metrics = sma2_complex.backtest_strategy(stock_list, sma_period, start_date, end_date, initial_balance, buy_sma, sell_sma)

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
        return render_template('SMA2_complex.html')