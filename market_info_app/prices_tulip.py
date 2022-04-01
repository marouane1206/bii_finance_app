import Config.config as config, sqlite3
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import date, timedelta
import numpy as np
import tulipy

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
    
    ## get data from alpaca api
    barsets = api.get_barset(symbol_chunk, 'day')

    for symbol in barsets:
        print(f"processing symbol {symbol}")
        
        # get closes from each symbol in barset for tulipy
        recent_closes = [bar.c for bar in barsets[symbol]]
        
        for bar in barsets[symbol]:
            stock_id = stock_dict[symbol]

            # tulipy calculations
            latest_day = date.today()-timedelta(days=1) 
            if len(recent_closes) >=50 and latest_day.isoformat() == bar.t.date().isoformat():
                sma_20 = tulipy.sma(np.array(recent_closes), period=20)[-1]
                sma_50 = tulipy.sma(np.array(recent_closes), period=50)[-1]
                rsi_14 = tulipy.rsi(np.array(recent_closes), period=14)[-1]
            else:
                sma_20, sma_50, rsi_14 = None, None, None

            # write to disk, sqlite3 db file
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v, sma_20, sma_50, rsi_14))

# commit changes to db
conn.commit()
