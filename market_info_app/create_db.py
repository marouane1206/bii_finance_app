import sqlite3, Config.config as config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            alpaca_id TEXT NOT NULL,
            exchange TEXT NOT NULL,
            easy_to_borrow BOOLEAN NOT NULL CHECK (easy_to_borrow IN (0, 1)),
            fractionable BOOLEAN NOT NULL CHECK (fractionable IN (0, 1)),
            marginable BOOLEAN NOT NULL CHECK (marginable IN (0, 1)),
            shortable BOOLEAN NOT NULL CHECK (shortable IN (0, 1))
        )
""")

cursor.execute("""
       CREATE TABLE IF NOT EXISTS stock_price (
           id INTEGER PRIMARY KEY, 
           stock_id INTEGER,
           date NOT NULL,
           open NOT NULL, 
           high NOT NULL, 
           low NOT NULL, 
           close NOT NULL, 
           volume NOT NULL,
           sma_20,
           sma_50,
           rsi_14,
           FOREIGN KEY (stock_id) REFERENCES stock (id)
)
""")


connection.commit()
