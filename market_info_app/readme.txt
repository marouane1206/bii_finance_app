# crontab -e

54 17 * * * /home/sean/miniconda3/envs/larry/bin/python /home/sean/gits    /mygits/larry/fstp/alpc_updatedb.py >> /home/sean/gits/mygits/larry/fstp    /update.log 2>&1

# sql query join
SELECT symbol, date, open, high, low, close
FROM stock_price 
JOIN stock on stock.id = stock_price.stock_id
WHERE symbol = 'AMC'
ORDER BY date;

# get_bars can only get single symbol, timeframe must use library: tradeapi.rest.TimeFrame.Day, .df to turn into df

# uvicorn command in development mode with reload
uvicorn main:app --reload

# Steps
## create_db.py to create sqlite3 db file
## populate_db.py to get list of tradable stock from alpaca
## prices.py to get day candles for 100 days for each stock from populate_db.py


