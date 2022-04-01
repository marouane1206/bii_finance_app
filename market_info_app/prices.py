import Config.config as config, sqlite3
import alpaca_trade_api as tradeapi
import pandas as pd

# connect to sqlite db file
conn = sqlite3.connect(config.DB_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# get list of symbols from sqlite db
cursor.execute("""
        SELECT id, symbol, name from stock
""")

rows = cursor.fetchall()

# setup mapping for symbol to stock_id
symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']


# connect to alpaca api
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

# Setup chunk size
chunk_size = 200

# get prices 200 symbols at a time
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]

    barsets = api.get_barset(symbol_chunk, 'day')

    for symbol in barsets:
        print(f"processing symbol {symbol}")
        for bar in barsets[symbol]:
            stock_id = stock_dict[symbol]
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))

# commit changes to db
conn.commit()
