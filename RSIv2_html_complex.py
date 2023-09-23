import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
from pytz import timezone
import matplotlib.pyplot as plt
from collections import defaultdict
import plotly.graph_objs as go
from plotly.subplots import make_subplots

API_KEY = 'PK3ABIZYDFUBONQF8FCW'
SECRET_KEY = 'sinlF6QYXaoVKA6Y6WFqTyx8zfYyuwrpwgO2WL7v'
BASE_URL = 'https://paper-api.alpaca.markets'



api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL, api_version='v2')

def plot_graphs(historical_data, buy_dates, buy_prices, sell_dates, sell_prices, start_date, end_date, buy_rsi, sell_rsi):
    close_prices = historical_data['close']
    date_range = historical_data.index

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Stock price", "RSI"), vertical_spacing=0.05, row_heights=[0.6, 0.4])

    # Stock prices
    fig.add_trace(go.Scatter(x=date_range, y=close_prices, mode='lines', name='Stock Price'), row=1, col=1)

    # RSI values
    rsi_values = historical_data['rsi']
    fig.add_trace(go.Scatter(x=date_range, y=rsi_values, mode='lines', name='RSI'), row=2, col=1)

    # RSI 35 and 70 lines
    fig.add_trace(go.Scatter(x=date_range, y=[buy_rsi]*len(rsi_values), mode='lines', name='RSI 35', line=dict(color='green', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=date_range, y=[sell_rsi]*len(rsi_values), mode='lines', name='RSI 70', line=dict(color='red', width=1)), row=2, col=1)

    # Buy dates and prices
    for stock, dates in buy_dates.items():
        fig.add_trace(go.Scatter(x=dates, y=buy_prices[stock], mode='markers', name=f'Buy ({stock})', marker=dict(color='limegreen', symbol='triangle-up')), row=1, col=1)
        rsi_buy_values = rsi_values.loc[dates]
        fig.add_trace(go.Scatter(x=dates, y=rsi_buy_values, mode='markers', name=f'Buy ({stock})', marker=dict(color='limegreen', symbol='triangle-up')), row=2, col=1)


    # Sell dates and prices
    for stock, dates in sell_dates.items():
        fig.add_trace(go.Scatter(x=dates, y=sell_prices[stock], mode='markers', name=f'Sell ({stock})', marker=dict(color='red', symbol='triangle-down')), row=1, col=1)
        rsi_sell_values = rsi_values.loc[dates]
        fig.add_trace(go.Scatter(x=dates, y=rsi_sell_values, mode='markers', name=f'Sell ({stock})', marker=dict(color='red', symbol='triangle-down')), row=2, col=1)


    # Update hover interaction
    fig.update_layout(hovermode='x unified')

    fig.update_layout(height=600, width=800, title_text='Stock Prices and RSI')
    return fig

'''def stock_list(input_str):
    # Split the string and convert each value to integer, creating an array
    stock_list = input_str.split()
    return stock_list'''

def get_historical_data(stock, start_date, end_date):
    bars = api.get_bars(stock, tradeapi.rest.TimeFrame.Day, start_date, end_date, limit=None, adjustment='raw').df
    return bars

def set_timeframe(start_date_str, end_date_str):
    # Convert start_date_str to a datetime object
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')

    # Convert end_date_str to a datetime object
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    # Convert the datetime objects to strings in the desired format
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    return start_date, end_date

#buy condition as function
def buy_condition(row, buy_rsi):
    buy_condition_met = False

    if row['rsi'] < buy_rsi:
        buy_condition_met = True

    return buy_condition_met

#sell condition
def sell_condition(stock, positions, row, sell_rsi):
    sell_condition_met = False

    if stock in positions and row['rsi'] > sell_rsi:
        sell_condition_met = True
    
    return sell_condition_met

def buy_stock(stock, num_shares, row, positions, cash, index):
    cash -= row['close'] * num_shares
    if stock not in positions:
        positions[stock] = {
            'num_shares': [num_shares],
            #purchase price includes price of all shares, this will change if I change share amount
            'purchase_price': [row['close']],
            'purchase_date': [index],
        }
    else:
        positions[stock]['num_shares'].append(num_shares)
        positions[stock]['purchase_price'].append(row['close'])
        positions[stock]['purchase_date'].append(index)
    
    return cash

def sell_stock(stock, row, positions, cash, trade_gains_losses, positions_sold, index, percent_gains_losses, trade_set):
    for i, purchase_price in enumerate(positions[stock]['purchase_price']):
        sold_price = row['close']
        sold_date = index
        
        trade_gains = sold_price * positions[stock]['num_shares'][i] - positions[stock]['purchase_price'][i]
        trade_gains_losses[stock].append(trade_gains)
        percent_gains = trade_gains / positions[stock]['purchase_price'][i]
        percent_gains_losses[stock].append(percent_gains)

        #dictionary with info about stocks once theyve been sold
        if stock not in positions_sold:
            positions_sold[stock] = {
            'sold_price': [sold_price],
            'purchase_price': [positions[stock]['purchase_price'][i]],
            'purchase_date': [positions[stock]['purchase_date'][i]],
            'sold_date' : [sold_date],
            'percent_gain' : [percent_gains],
            'trade_gains' : [trade_gains],
            'trade_set' : [trade_set],
            'trade_count' : [i+1]  # Add trade_count to track the trade count within the trade set
            }
        else:
            positions_sold[stock]['sold_price'].append(sold_price)
            positions_sold[stock]['purchase_price'].append(positions[stock]['purchase_price'][i])
            positions_sold[stock]['purchase_date'].append(positions[stock]['purchase_date'][i])
            positions_sold[stock]['sold_date'].append(sold_date)
            positions_sold[stock]['percent_gain'].append(percent_gains)
            positions_sold[stock]['trade_gains'].append(trade_gains)
            positions_sold[stock]['trade_set'].append(trade_set)
            positions_sold[stock]['trade_count'].append(i+1)
                
    cash += row['close'] * sum(positions[stock]['num_shares'])
    del positions[stock]
    return cash

def calculate_open_positions_value(positions, stock_prices):
    open_positions_value = {} # dict that include open positions and their symbols and values
    open_summs = {}
    total_open_positions_value = 0 # total $ total of open positons
    current_price = 0
    number_of_open_shares = 0

    for stock, data in positions.items():
        number_of_open_shares = sum(data['num_shares'])
        current_price = stock_prices[stock][-1]
        open_positions_value[stock] = number_of_open_shares * current_price
        total_open_positions_value += open_positions_value[stock]
    
    open_summs['Total value'] = total_open_positions_value
    open_summs['Current price'] = current_price
    open_summs['# of open shares'] = number_of_open_shares

    return open_summs

#makes trades a list of dicts per trade, and creates a dataframe
def create_trades_dfs(stock, positions, positions_sold, stock_prices, end_date, trade_set):
    trades_metrics = []
    if positions_sold.get(stock) is not None:
        for i, _ in enumerate(positions_sold[stock]['purchase_price']):
            trade = {
                'trade_id': f"{positions_sold[stock]['trade_set'][i]}.{positions_sold[stock]['trade_count'][i]}",
                'stock': stock.capitalize(),
                'purchase_date': positions_sold[stock]['purchase_date'][i].date(),
                'purchase_price': positions_sold[stock]['purchase_price'][i],
                'sold_date': positions_sold[stock]['sold_date'][i].date(),
                'sold_price': positions_sold[stock]['sold_price'][i],
                'trade_gains': positions_sold[stock]['trade_gains'][i],
                'percent_gain': positions_sold[stock]['percent_gain'][i] * 100
            }
            trades_metrics.append(trade)
    closed_df = pd.DataFrame(trades_metrics)
    
    open_data = []
    for stock, data in positions.items():
        last_price = stock_prices[stock][-1]
        last_date = end_date[:10]
        trade_num = 0
        for i in range(len(data['purchase_date'])):
            purchase_date = data['purchase_date'][i].date()
            purchase_price = data['purchase_price'][i]
            trade_gains = last_price - purchase_price
            percent_gains = (last_price / purchase_price - 1) * 100
            trade_num += 1
            trade_id = f"{trade_set+1}.{trade_num}"
            open_data.append([trade_id, stock, purchase_date, purchase_price, last_date, last_price, trade_gains, percent_gains])
    open_df = pd.DataFrame(open_data, columns=['trade_id', 'stock', 'purchase_date', 'purchase_price', 'last_date', 'last_price', 'trade_gains', 'percent_gains'])
    
    return closed_df, open_df

def better_metrics(initial_balance, final_balance, closed_df, open_df, open_summs):
    final_metrics = {}

    # general
    final_metrics['total_invested'] = closed_df['purchase_price'].sum()
    final_metrics['total_sold'] = closed_df['sold_price'].sum()

    # portfolio
    final_metrics['initial_balance'] = initial_balance
    final_metrics['final_balance'] = final_balance
    final_metrics['portfolio_change_$'] = (final_balance - initial_balance)
    final_metrics['portfolio_change_%'] = ((final_balance - initial_balance) / initial_balance) * 100

    # closed positions
    final_metrics['total_$_gain'] = closed_df['trade_gains'].sum()
    final_metrics['mean_$_gain'] = closed_df['trade_gains'].mean()
    final_metrics['total_%_gain_of_invested'] = ((final_metrics['total_sold'] - final_metrics['total_invested']) / final_metrics['total_invested']) * 100
    final_metrics['ave_%_gain'] = closed_df['percent_gain'].mean()
    final_metrics['var_%_gain'] = closed_df['percent_gain'].var()
    final_metrics['stdvar_%_gain'] = closed_df['percent_gain'].std()
    final_metrics['closed_trade_count'] = closed_df['trade_gains'].count()


    # open positions
    final_metrics['open_shares_price'] = open_summs['Current price']
    final_metrics['#_of_open_shares'] = open_summs['# of open shares']
    final_metrics['value_of_open_shares'] = open_summs['Total value']

    return final_metrics    

#function to display final metrics
def final_metrics(final_balance, initial_balance, stock, positions, trade_gains_losses, percent_gains_losses, stock_prices, closed_df, open_df):
    final_metrics = {}

    # Open Metrics
    for stock in positions:
        for i, price in enumerate(positions[stock]['purchase_price']):
            final_metrics[f"{stock}_open_shares_price"] = stock_prices[stock][-1]  # Use current price for open positions

    # Include final value of any open positions
    for stock, data in positions.items():
        num_shares = sum(data['num_shares'])
        current_price = stock_prices[stock][-1]
        final_metrics[f"{stock}_open_shares_value"] = num_shares * current_price
        final_metrics[f"{stock}_num_open_shares"] = num_shares

    # Closed Metrics
    # Total gains/losses
    for stock in trade_gains_losses:
        final_metrics[f"{stock}_total_gains_losses"] = sum(trade_gains_losses[stock])
        final_metrics[f'{stock}_num_of_complete_trades'] = len(trade_gains_losses[stock])
        final_metrics[f"{stock}_ave_gains_losses"] = final_metrics[f"{stock}_total_gains_losses"] / final_metrics[f'{stock}_num_of_complete_trades']

    for stock, gains in percent_gains_losses.items():
        final_metrics[f'{stock}_ave_efficiency'] = sum(gains) / len(gains)
        final_metrics[f'{stock}_total_efficiency'] = sum(gains)

    # Portfolio change metrics
    final_metrics['initial_balance'] = initial_balance
    final_metrics['final_balance'] = final_balance
    final_metrics['profit_percent'] = ((final_balance - initial_balance) / initial_balance) * 100
    final_metrics['profit_absolute'] = final_balance - initial_balance

    # Average Holding Period for Open Positions
    if not open_df.empty:
        open_df['last_date'] = pd.to_datetime(open_df['last_date'])
        open_df['purchase_date'] = pd.to_datetime(open_df['purchase_date'])
        avg_holding_period = (open_df['last_date'] - open_df['purchase_date']).mean().days
    else:
        avg_holding_period = 0
    final_metrics['Average Holding Period for Open Positions'] = avg_holding_period

    return final_metrics

def rsi(data, rsi_period):
    periods=rsi_period
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def backtest_strategy(stock_list, rsi_period, start_date_str, end_date_str, inital_balance, buy_rsi, sell_rsi):

    start_date, end_date = set_timeframe(start_date_str, end_date_str)

    trade_gains_losses = defaultdict(list)
    percent_gains_losses = defaultdict(list)
    stock_prices = defaultdict(list)
    rsi_values = defaultdict(list)

    buy_dates = defaultdict(list)
    buy_prices = defaultdict(list)
    sell_dates = defaultdict(list)
    sell_prices = defaultdict(list)


    cash = inital_balance  # Initialize the amount of cash you have
    num_shares = 1
    positions = {}  # The stocks you currently own
    positions_sold = {}
    trade_set = 0 #tells you what group of trades you are on for the stock (all stocks in one group are sold together)

    initial_balance = cash  # Keep track of your initial balance

    for stock in stock_list:
        historical_data = get_historical_data(stock, start_date, end_date)
        historical_data['rsi'] = rsi(historical_data['close'], rsi_period)
        
        for index, row in historical_data.iterrows():
            if pd.isna(row['rsi']):
                continue
            #buy and sell conditions
            if buy_condition(row, buy_rsi):
                cash = buy_stock(stock, num_shares, row, positions, cash,  index)
                buy_dates[stock].append(pd.to_datetime(index))
                buy_prices[stock].append(row['close'])
            elif sell_condition(stock, positions, row, sell_rsi):
                trade_set += 1
                cash = sell_stock(stock, row, positions, cash, trade_gains_losses, positions_sold, index, percent_gains_losses, trade_set)
                sell_dates[stock].append(pd.to_datetime(index))
                sell_prices[stock].append(row['close'])
            stock_prices[stock].append(row['close'])
            rsi_values[stock].append(row['rsi'])

    #plots displayed on site
    fig = plot_graphs(historical_data, buy_dates, buy_prices, sell_dates, sell_prices, start_date, end_date, buy_rsi, sell_rsi)

    #creates dict with opensum info
    open_summs =  calculate_open_positions_value(positions, stock_prices)

    #create dataframe of open positions dict
    closed_df, open_df = create_trades_dfs(stock, positions, positions_sold, stock_prices, end_date, trade_set)

    final_balance = cash + open_summs['Total value']

    final_metrics = better_metrics(initial_balance, final_balance, closed_df, open_df, open_summs)

    return final_balance, initial_balance, stock, positions, trade_gains_losses, positions_sold, closed_df, open_df, percent_gains_losses, fig, stock_prices, final_metrics

if __name__ == '__main__':
    stocks = input("Enter stocks separated by space: ")
    final_balance, initial_balance, stock, positions, trade_gains_losses, positions_sold, closed_df, open_df, percent_gains_losses, fig, stock_prices, final_metrics = backtest_strategy(stocks)