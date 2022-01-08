import websocket
import threading
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# User inputted stock tickers for data collection and plotting.
tickers = input('Enter stock symbols: ')
tickers = tickers.split(' ')

# This dataframe will store the price data for all the tickers.
df_columns = []
for ticker in tickers:
    df_columns.append('B-' + ticker)
    df_columns.append('A-' + ticker)
df = pd.DataFrame(columns=df_columns)

# Create the plot for each ticker with some presets.
fig, ax = plt.subplots(1, len(tickers))
plt.style.use('seaborn-dark-palette')
fig.patch.set_facecolor('gainsboro')

def on_open(ws):
    """
    This function runs after the WebSocket connection is opened. This function authenticates the connection with
    the alpaca using the public and private keys. Then a market data subscription message is sent.
    :param ws: WebSocket Object
    """

    authenticate = {"action": "auth", "key": "{public key}", "secret": "{secret key}"}
    ws.send(json.dumps(authenticate))

    subscribe = {"action": "subscribe", "quotes": tickers}
    ws.send(json.dumps(subscribe))

def on_message(ws,message):
    """
    This function runs after a message is sent to us from the WebSocket server. This message is loaded using
    json and is sent to another function for processing.
    :param ws: WebSocket Object
    :param message: The message sent from the WebSocket Server.
    """

    message = json.loads(message)
    process_message(message)

def process_message(message):
    """
    This function processes the message sent from the WebSocket. If the message is stock price data, the bid and ask
    prices will be appended to the corresponding stock column in the main dataframe.
    :param message: The message sent from the WebSocket Server.
    """

    global df

    for item in message:
        if item['T'] == 'q':
            symbol = item['S']
            bid = item['bp']
            ask = item['ap']

            if not df.empty:
                df_append = pd.DataFrame({'B-' + symbol: bid, 'A-' + symbol: ask}, index=[df.index[-1] + 1])
            else:
                df_append = pd.DataFrame({'B-' + symbol: bid, 'A-' + symbol: ask}, index=[0])

            df = df.append(df_append)

def wsthread():
    """
    This function creates the WebSocket connection with Alpaca Markets.
    Possible WebSocket connections:
    wss://stream.data.alpaca.markets/v1beta1/crypto?exchanges=FTX
    wss://stream.data.alpaca.markets/v2/sip
    """
    ws = websocket.WebSocketApp("wss://stream.data.alpaca.markets/v1beta1/crypto?exchanges=FTX",
                                on_open=on_open,
                                on_message=on_message)
    ws.run_forever()

# Enables WebSocket data collection and real time plotting to run concurrently.
t = threading.Thread(target=wsthread)
t.start()

def animate(i):
    """
    This function plots all the ticker data in real time.
    """

    global df

    for count, tic in enumerate(tickers):

        data = df[['B-'+tic, 'A-'+tic]]
        data.dropna(inplace=True)
        data.reset_index(drop=True, inplace=True)
        data = data[-10000:]

        ax[count].cla()
        ax[count].set_title(tic, loc='LEFT')
        ax[count].set_prop_cycle(color=['forestgreen', 'firebrick'])
        ax[count].margins(x=0)
        ax[count].axes.get_xaxis().set_ticks([])
        ax[count].step(data.index, data)

        if not data.empty:
            df = df.append(data.iloc[-1], ignore_index=True)

# Real time plot.
ani = FuncAnimation(plt.gcf(), animate, interval=0)
plt.show()
