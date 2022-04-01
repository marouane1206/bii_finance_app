import psycopg2
import alpaca_trade_api as tradeapi
import Config.config as config

# use absolute path for db file if using cronjob
connection = sqlite3.connect(config.DB_FILE)

# return rows as sqlite3 object
connection.row_factory = sqlite3.Row

cursor = connection.cursor()
cursor.execute("""
        SELECT symbol, name FROM stock
        """)
rows = cursor.fetchall()

# setup list of collected symbols in db
symbols = [row['symbol'] for row in rows]

# connect to alpaca api
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL) #, raw_data=True)

# get list of alpaca tradables
assets = api.list_assets(status='active')
    
# Check if any new symbols
for asset in assets:
    try:
#        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
        if asset.tradable and asset.symbol not in symbols:
            print(f"new stock: {asset.symbol} , {asset.name}")
            cursor.execute("""INSERT INTO stock (
            symbol, 
            name, 
            alpaca_id, 
            exchange, 
            easy_to_borrow, 
            fractionable, 
            marginable, 
            shortable
            ) VALUES (?,?,?,?,?,?,?,?)""", 
            (asset.symbol, 
                asset.name, 
                asset.id, 
                asset.exchange, 
                asset.easy_to_borrow, 
                asset.fractionable, 
                asset.marginable, 
                asset.shortable))
    except Exception as e:
        print(f"{e} : for : {asset.symbol}")

print("Done....")
connection.commit()
