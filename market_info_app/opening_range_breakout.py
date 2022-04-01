import sqlite3, Config.config as config
import alpaca_trade_api as tradeapi
import datetime as date
import smtplib, ssl    # * email
from timezone import is_dst


# Create a secure SSL context * email
context = ssl.create_default_context()

# def send_email():
#     with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#         server.login("my@gmail.com", password)
#         # TODO: Send email here

connection =sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
    select id from strategy where name = 'opening_range_breakout'
    """)

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    select symbol, name from stock join stock_strategy on stock_strategy.stock_id = stock.id where stock_strategy.strategy_id = ?
    """, (strategy_id,)) 
# params must be tuple

stocks = cursor.fetchall()

symbols = [stock['symbol'] for stock in stocks]
symbols = list(set(symbols))
print(symbols)

# api stuff to alpaca
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
minute = tradeapi.rest.TimeFrame.Minute
current_date = "2021-08-13" #(date.today()-date.timedelta(days=3)).isoformat()
start_minute_bar = f"{current_date} 13:30:00"
end_minute_bar = f"{current_date} 13:45:00"
print(start_minute_bar)

# Sending Orders, limit them from repeating
# orders = api.list_orders(status='all', limit=50, after=f"{current_date}T13:30:00Z")
# existing_order_symbols = [order.symbol for order in orders]

# to collect alerts triggered by signal
alerts = []

#api.get_bars()
for symbol in symbols:
    minute_bars = api.get_bars(symbol, minute, start=current_date, end=current_date).df
    print(symbol)
    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    # print(opening_range_bars)

    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    print(opening_range_low)
    print(opening_range_high)
    # print(opening_range)

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    # print(after_opening_range_bars)

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        # print(f" BREAKOUT: {after_opening_range_breakout}")
        limit_price = after_opening_range_breakout.iloc[0]['close']
        # print(f"ENTRY: {limit_price}")
        # print(f"EXIT: {after_opening_range_bars['high'].max()}")
        alert_msg = f"{symbol}, Entry: {limit_price}, Profit: {after_opening_range_bars['high'].max()}"
        alerts.append(alert_msg)

mystr = "\n\n".join(alerts)
print("\n".join(alerts))

# Actual part that sends the email
with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    email_msg = f"Subject: Breakout Notify for {current_date}\n\n"
    email_msg += "\n".join(alerts)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_msg)

# close sqlite3 handle
cursor.close()
connection.close()


