import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
from pytz import timezone
import matplotlib.pyplot as plt
from collections import defaultdict
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio

API_KEY = 'PK3ABIZYDFUBONQF8FCW'
SECRET_KEY = 'sinlF6QYXaoVKA6Y6WFqTyx8zfYyuwrpwgO2WL7v'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL, api_version='v2')

stock_list = ["SPY", "QQQ", "DIA"]

def plot_last_year_prices(stock_list):

    plots = defaultdict()

    start_date = (datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(days=365)).strftime(
        '%Y-%m-%d')
    end_date = (
        datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(minutes=15)).strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    
    for stock in stock_list:
        fig = make_subplots(rows=1, cols=1, subplot_titles=stock)
        
        historical_data = get_historical_data(stock, start_date, end_date)
        trace = go.Scatter(x=historical_data.index, y=historical_data['close'], mode='lines', name=stock)
        fig.add_trace(trace, row=1, col=1)
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)

        fig.update_layout(height=600, width=800, title_text=f'Last Year Prices - {stock}')
        
        # Store the plot in the dictionary
        plots[stock] = fig.to_dict()

    return plots
    
def get_historical_data(stock, start_date, end_date):
    bars = api.get_bars(stock, tradeapi.rest.TimeFrame.Day, start_date, end_date, limit=None, adjustment='raw').df
    return bars

if __name__ == '__main__':
    
    plots = plot_last_year_prices(stock_list)
    
    # Display the plots
    for stock, plot_data in plots.items():
        pio.show(plot_data)
