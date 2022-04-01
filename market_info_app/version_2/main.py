import Config.config as config
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from market_info_app.version_2.createdb import Stock, engine, Stock_Price
from sqlmodel import Session, select, func
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd


# 1) Instantiate fastapi server instance
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware stuff
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def getprice(symbol):
    with Session(engine) as session:
        stmt = select(Stock.id, Stock.symbol, Stock.name, Stock.exchange).where(Stock.symbol==symbol)    
        row = session.exec(stmt).first() 

        stmt = select(Stock_Price
            ).join(Stock, Stock.id==Stock_Price.stock_id
            ).where(Stock_Price.stock_id==row.id
            ).order_by(Stock_Price.date.desc())
        prices = session.exec(stmt).all()
    return row, prices


async def stocklist(stklist):
    with Session(engine) as session:
        last_date = session.exec(func.max(Stock_Price.date)).first()
        if stklist == "new_closing_highs":
                 
            subq = select(Stock.id,
                        Stock.symbol, 
                        Stock.name,
                        func.max(Stock_Price.close).label('close'),
                        Stock_Price.date
                        ).join(Stock_Price, Stock.id==Stock_Price.stock_id
                            ).group_by(Stock.id).subquery()
            stmt = select(subq.c.id,
                        subq.c.symbol,
                        subq.c.name,
                        subq.c.close,
                        subq.c.date).where(subq.c.date==last_date[0]
                        ).order_by(subq.c.symbol)
        elif stklist== "new_closing_lows":    
            subq = select(Stock.id,
                        Stock.symbol, 
                        Stock.name,
                        func.min(Stock_Price.close).label('close'),
                        Stock_Price.date
                        ).join(Stock_Price, Stock.id==Stock_Price.stock_id
                            ).group_by(Stock.id).subquery()
            stmt = select(subq.c.id,
                        subq.c.symbol,
                        subq.c.name,
                        subq.c.close,
                        subq.c.date).where(
                subq.c.date==last_date[0]).order_by(subq.c.symbol)
        else:
            subq = select(Stock.id,
                        Stock.symbol, 
                        Stock.name,
                        Stock_Price.close,
                        Stock_Price.date
                        ).join(Stock_Price, Stock.id==Stock_Price.stock_id
                            ).group_by(Stock.id).subquery()
            stmt = select(subq.c.id,
                        subq.c.symbol,
                        subq.c.name,
                        subq.c.close,
                        subq.c.date).order_by(subq.c.symbol)  

        rows = session.exec(stmt).all() 
    return rows


@app.get('/')
async def home(request: Request):

    stock_filter = request.query_params.get('filter', False)
    print("**** GOTTEN: ", stock_filter)
    rows = await stocklist(stock_filter)
    result = {'length':len(rows)}

    return templates.TemplateResponse("home.html", {"request": request, "stocks":rows, 'result':result}) 


@app.get("/stock/{symbol}")
async def home(request: Request, symbol):

    row, prices = await getprice(symbol)

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stonk":row, "pricing":prices})


@app.get("/history")
async def history(symbol):
    row, prices = await getprice(symbol)
    proc_candles = [{ 
        "time": (candle.date).isoformat()[:10], 
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close} for candle in prices]
    proc_candles.reverse()
    return proc_candles