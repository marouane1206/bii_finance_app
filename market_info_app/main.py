import sqlite3, Config.config as config
import alpaca_trade_api as tradeapi
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import date, timedelta

# TODO:factor out sql connection with sqlalchemy

# 1) Instantiate fastapi server instance
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# 4) Instantiate templating object
templates = Jinja2Templates(directory="templates")


# 2) Start placing endpoints this is 1st endpoint.
@app.get('/')
def home(request: Request):    # 5) process requests 

    # 6) process filter request
    stock_filter = request.query_params.get('filter', False)

    # 3) connect to sqlite db file and retrieve stuf
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # filter sql read based on filter
    if stock_filter == "new_closing_highs":
        cursor.execute("""
            SELECT * FROM (
                SELECT stock.id, symbol, name, stock_id, max(close), date
                FROM stock_price join stock on stock.id = stock_price.stock_id
                group by stock_id
                order by symbol
                ) where date = (select max(date) from stock_price)
        """) #, ((date.today() - timedelta(days=1)).isoformat(),))

    elif stock_filter == "new_closing_lows":
        cursor.execute("""
            SELECT * FROM (
                SELECT stock.id, symbol, name, stock_id, min(close), date
                FROM stock_price join stock on stock.id = stock_price.stock_id
                group by stock_id
                order by symbol
                ) where date = (select max(date) from stock_price)
        """) #, ((date.today() - timedelta(days=1)).isoformat(),))

    elif stock_filter == "rsi_overbought":
        cursor.execute("""
            SELECT stock.id, symbol, name, stock_id, date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 > 70
            AND date = (select max(date) from stock_price)
            order by symbol
        """)

    elif stock_filter == "rsi_oversold":
        cursor.execute("""
            SELECT stock.id, symbol, name, stock_id, date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 < 30
            AND date = (select max(date) from stock_price)
            order by symbol
        """)

    else:
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
        """)

    rows = cursor.fetchall()
    
    # get indicator values
#    latest_day = date.today() - timedelta(days=1)
    cursor.execute("""
    select symbol, rsi_14, sma_20, sma_50, close
    from stock join stock_price on stock_price.stock_id = stock.id
    where date = (select max(date) from stock_price)
    """,) # (latest_day.isoformat(),))

    indicator_rows = cursor.fetchall()
    indicator_values = {}

    for row in indicator_rows:
        indicator_values[row['symbol']] = row

    # return templates response containing request object
    return templates.TemplateResponse("home.html", {"request": request, "stocks":rows, "indicator_values": indicator_values}) 


# dynamic endpoint link for each stock symbol
@app.get("/stock/{symbol}")
def home(request: Request, symbol):
    # 3) connect to sqlite db file and retrieve stuf
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # strategies part
    cursor.execute("""
        SELECT * FROM strategy
        """)
    strategies = cursor.fetchall()
    
    # fetch selected symbol info from sqlite database
    cursor.execute("""
        SELECT id, symbol, name, exchange FROM stock WHERE symbol = ? 
    """, (symbol,))
    row = cursor.fetchone()
    
    # fetch selected symbol price from price table
    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC
    """,(row['id'],))
    prices = cursor.fetchall()

    # return templates response containing request object
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stonk":row, "pricing":prices, "strategies":strategies})


@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?,?)
        """, (stock_id, strategy_id))
#    cursor.execute("""
#        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?,?)   
#        WHERE NOT EXISTS (SELECT *
#              FROM stock_strategy
#              WHERE stock_strategy.stock_id = ? AND stock_strategy.strategy_id = ?)
#    """,(stock_id, strategy_id, stock_id, strategy_id))

    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)


# strategies page
@app.get("/strategies")
def strategies(request:Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM strategy
        """)
    strategies = cursor.fetchall()
    return templates.TemplateResponse("strategies.html", {"request": request, "strategies":strategies})


# orders page
@app.get("/orders")
def orders(request:Request):
    # get data directly from alpaca api
    api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
    orders = api.list_orders(status='all')
    return templates.TemplateResponse("orders.html", {"request": request,"orders":orders})


# strategy id page
@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, name FROM strategy WHERE id =?
        """, (strategy_id,))
    strategy = cursor.fetchall()

    cursor.execute("""
        SELECT symbol, name FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id WHERE strategy_id = ?
        """, (strategy_id,))
    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})
