from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.encoders import jsonable_encoder
# from sqlmodel import Session, select
from typing import Optional, List

# import pandas as pd
import Config.config as config
# import alpaca_trade_api as tradeapi
from market_info_app.version_2.createdb import Stock, engine, Stock_Price
from sqlmodel import Session, select, func
# api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
CHUNK_SIZE = 200

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


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    title = "coinview"
    header1 = "SHAKENAIAH"
    return templates.TemplateResponse("index.html", {"request": request, "title":title, "header1":header1})


@app.get('/history')
async def history():
    symbol="AMC"
    with Session(engine) as session:
        stmt = select(Stock.id, Stock.symbol, Stock.name, Stock.exchange).where(Stock.symbol==symbol)    
        row = session.exec(stmt).first() 

        stmt = select(Stock_Price
            ).join(Stock, Stock.id==Stock_Price.stock_id
            ).where(Stock_Price.stock_id==row.id
            ).order_by(Stock_Price.date.desc())
        prices = session.exec(stmt).all()
    
    proc_candles = [{ 
        "time": (candle.date).isoformat()[:10], 
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close} for candle in prices]
    proc_candles.reverse()
    return proc_candles
    
