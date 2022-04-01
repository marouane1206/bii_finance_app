from sqlmodel import Session, select, func
import alpaca_trade_api as tradeapi

from market_info_app.version_2.createdb import Stock, engine, Stock_Price
import Config.config as config
import pandas as pd


# Setup api and chunk_size
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
CHUNK_SIZE = 200


def get_stocks():
    """get list of alpaca active symbols"""
    assets = api.list_assets(status='active')
    return assets


def create_stocks():
    """insert stocks details into stock table"""
    assets = get_stocks()
    with Session(engine) as session:
        symbols = session.exec(select(Stock.symbol)).all()
        for asset in assets:
            try:
                if asset.tradable and asset.symbol not in symbols:
                    print(f"new stock: {asset.symbol}, {asset.name}")
                    asset = Stock( 
                            symbol=asset.symbol,
                            name=asset.name,
                            alpaca_id=asset.id,
                            exchange=asset.exchange,
                            easy_to_borrow=asset.easy_to_borrow,
                            fractionable=asset.fractionable,
                            marginable=asset.marginable,
                            shortable=asset.shortable)
                    session.add(asset)
            except Exception as e:
                print(f"{e} : for : {asset.symbol}")
        session.commit()


def read_stocklist():
    """get list and dict{sym:id} of all stocks"""
    symbols = []
    stock_dict = {}
    with Session(engine) as session:
        rows = session.exec(select(Stock.symbol, Stock.id)).all()
        for row in rows:
            symbol = row['symbol']
            symbols.append(symbol)
            stock_dict[symbol] = row['id']
    return symbols, stock_dict


def get_date_after():
    with Session(engine) as session:
        result = session.exec(select(func.max(Stock_Price.date))).first()
        result = pd.Timestamp(result, tz='US/Eastern')
        result = result.isoformat()
    return result
        

def get_update_prices():
    symbols, stock_dict = read_stocklist()
    # symbols = 'AMC'
    after = get_date_after()

    with Session(engine) as session:
        for i in range(0, len(symbols), CHUNK_SIZE):
            symbol_chunk = symbols[i:i+CHUNK_SIZE]
            if after:
                barsets = api.get_barset(symbol_chunk, 'day', after=after)
            else:
                barsets = api.get_barset(symbol_chunk, 'day')
            for symbol in barsets:
                print(f"Processing symbol {symbol}")
                for bar in barsets[symbol]:
                    price = Stock_Price(
                            stock_id=stock_dict[symbol],
                            date=bar.t,
                            open=bar.o,
                            high=bar.h,
                            low=bar.l,
                            close=bar.c,
                            volume=bar.v)
                    session.add(price)
            session.commit()
        
        
def main():
#    print("No main() setted")
    # dt = get_date_after()
    # print("****** ANSWER: ",dt, type(dt))
    get_update_prices()

if __name__ == "__main__":
    main()
