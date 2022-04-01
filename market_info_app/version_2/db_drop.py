import sqlite3

db_filename = "database.db"
connection = sqlite3.connect(db_filename)

cursor = connection.cursor()

cursor.execute("DROP TABLE stock_price")
cursor.execute("DROP TABLE stock")


connection.commit()
