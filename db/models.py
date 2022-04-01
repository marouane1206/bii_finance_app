############################################################################
########### ENV IMPORTS ####################################################
# SQLModel imports
from sqlmodel import SQLModel, Field, Column, VARCHAR, create_engine, UniqueConstraint, DateTime, Session
from typing import Optional
from pydantic import condecimal

from dataclasses import dataclass

# system imorts
from datetime import datetime
import sys
import requests

# database libraries
import financedatabase as fd
import pycountry
from hdx.location.country import Country

from bs4 import BeautifulSoup

########### BII_FINANCE IMPORTS ############################################
from Config import DB_Params
from xcas_companies import Get_XCAS_Companies

#############################################################################
########### SQLMODEL classes ################################################
class Currencies(SQLModel, table=True):
    currency_id: str = Field(primary_key=True)
    currency_name: str
    currency_numeric: int    

class Countries(SQLModel, table=True):
    country_id: str = Field(primary_key=True)
    country_alpha_3: str
    country_flag: str
    country_name: str
    country_numeric: int

class Currency_Countries(SQLModel, table=True):
    country_id: str =Field(primary_key=True)
    currency_id: str
    country_name: str
    __table_args__ = (UniqueConstraint("currency_id", "country_id"),)

class Stock_Countries(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(sa_column=Column("symbol", VARCHAR, unique=True))
    short_name: Optional[str]
    long_name: Optional[str]
    currency: Optional[str] = Field(default=None, foreign_key="currencies.currency_id")
    sector: Optional[str]
    industry: Optional[str]
    exchange: Optional[str]
    market: Optional[str]
    country: Optional[str] = Field(default=None, foreign_key="countries.country_id")
    city: Optional[str]
    website: Optional[str]
    market_cap: Optional[str]
    __table_args__ = (UniqueConstraint("symbol", "country"),)    

class ETFs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(sa_column=Column("symbol", VARCHAR, unique=True))
    short_name: Optional[str]
    long_name: Optional[str]
    currency: Optional[str] = Field(default=None, foreign_key="currencies.currency_id")
    summary: Optional[str]
    category: Optional[str]
    family: Optional[str]
    exchange: Optional[str]
    market: Optional[str]
    total_assets: condecimal(max_digits=5, decimal_places=3) = Field(default=0)

class Indices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(sa_column=Column("symbol", VARCHAR, unique=True))
    short_name: Optional[str]
    market: Optional[str]
    exchange: Optional[str]
    currency: Optional[str] = Field(default=None, foreign_key="currencies.currency_id")
    exchange_timezone: Optional[str]
    __table_args__ = (UniqueConstraint("symbol", "currency"),)

class Stock_Prices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: Optional[int] = Field(default=None, foreign_key="stock_countries.id")
    date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    open: float
    high: float
    low: float
    close: float
    volume: int
    __table_args__ = (UniqueConstraint("stock_id", "date"),)
    
class Strategies(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=None,nullable=False)

class Stock_Strategies(SQLModel, table=True):
    id: Optional[int] = Field(default=None,primary_key=True)
    stock_id: Optional[int] = Field(default=None, foreign_key="stock_countries.id")
    strategy_id: Optional[int] = Field(default=None, foreign_key="strategies.id")


##### TO DO LIST ######################################################################
fd_currencies = fd.select_currencies()
fd_cryptocurrencies = fd.select_cryptocurrencies()
fd_funds = fd.select_funds()
#fd_money_market = fd.select_moneymarket()

#######################################################################################
############### Connect to PostgreSQL #################################################
postgresql_url = f"postgresql+psycopg2://{self.params['user']}:{self.params['password'].replace('@','%40')}@{self.params['host']}/{self.params['database']}"
# Remove echo on production
engine = create_engine(postgresql_url, echo=False)

#######################################################################################
############## Functions section ######################################################
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def add_currencies():
    currencies = list(pycountry.currencies)
    for curncy in currencies: 
        with Session(engine) as session:
            currency = Currencies(
                currency_id = curncy.alpha_3, 
                currency_name = curncy.name,
                currency_numeric = curncy.numeric)
            session.add(currency)
            session.commit()
            print(f"Al 7amdu Lillah Currency : {curncy.alpha_3} updated !!!!!!")

def add_countries():
    countries = list(pycountry.countries)
    for cntry in countries:    
        with Session(engine) as session:
            country= Countries(
                country_id = cntry.alpha_2, 
                country_alpha_3 = cntry.alpha_3,
                country_flag = cntry.flag,
                country_name = cntry.name,
                country_numeric = cntry.numeric)
            session.add(country)
            session.commit()
            print(f"Al 7amdu Lillah, {cntry.name} updated !!!!!!")
            
    netherlands_antilles = Countries(
        country_id = 'AN', 
        country_alpha_3 = 'ANT',
        country_flag = 'an',
        country_name = 'Netherlands Antilles',
        country_numeric = 530)
    session.add(netherlands_antilles)
    session.commit()
    print(f"Al 7amdu Lillah 'Netherlands Antilles' updated !!!!!!")

def add_currency_countries():
    currcy_ctry = list(pycountry.countries)
    for cntry in currcy_ctry:
        if cntry.alpha_2 == 'AQ':
            currency_id = 'XXX'
        else:
            currency_id = Country.get_currency_from_iso3(cntry.alpha_3)
        
        with Session(engine) as session:
            curcontrries = Currency_Countries(
                country_id = cntry.alpha_2, 
                currency_id = currency_id, 
                country_name = cntry.name)
            session.add(curcontrries)
            session.commit()
            print(f"Al 7amdu Lillah Currency : {currency_id} of {cntry.name} updated !!!!!!")

def clean_countries(country):
    if country.upper() == 'MACAU':
        country = 'macao'
    if country.upper() == 'NETHERLANDS ANTILLES':
        country = 'Sint Maarten (Dutch part)'
    return country

def add_stock_countries():
    stocks = fd.select_equities()

    for stock,info in stocks.items():
        if info['country'] is not None:
            country_cln = pycountry.countries.search_fuzzy(clean_countries(info['country']))
            country_cln = country_cln[0].alpha_2
        with Session(engine) as session:
            if stock != '':
                stock_cntry = Stock_Countries(
                    symbol = stock,
                    short_name = info['short_name'], 
                    long_name = info['long_name'], 
                    currency = info['currency'],
                    sector = info['sector'],
                    industry = info['industry'],
                    exchange = info['exchange'],
                    market = info['market'],
                    city = info['city'],
                    website = info['website'],
                    market_cap = info['market_cap'],
                    country = country_cln
                    )
                session.add(stock_cntry)
                session.commit()
                print(f"Al 7amdu Lillah Stock : {stock} from : {country_cln} updated !!!!!!")

def add_companies_xcas():
    xcas = Get_XCAS_Companies()
    for stock,info in xcas.items():
        with Session(engine) as session:
            if stock != '':
                company_xcas = Stock_Countries(
                    symbol = linfo['Code ISIN'],
                    short_name = info['Libelle instrument'], 
                    long_name = info['Libelle instrument'], 
                    currency = 'MAD',
                    sector = info['Secteur/Catégorie'],
                    industry = info['Secteur/Catégorie'],
                    exchange = 'XCAS',
                    market = 'morocco_market',
                    city = 'Casablanca',
                    website = 'https://www.casablanca-bourse.com/Bourseweb/index.aspx',
                    market_cap = info['Nombre de titre formant le capital'],
                    country = 'MA'
                    )
            session.add(company_xcas)
            session.commit()
            print(f"Al 7amdu Lillah Stock : {short_name} from : {sector} updated !!!!!!")

def add_etfs():
    etfs = fd.select_etfs()
    
    for symbol,info in etfs.items():
        with Session(engine) as session:
            if symbol != '':
                etf_symbol = ETFs(
                    symbol = symbol,
                    short_name =  info['short_name'],
                    long_name =  info['long_name'],
                    currency =  info['currency'],
                    country = 'US',
                    summary =  info['summary'],
                    category =  info['category'],
                    family =  info['family'],
                    exchange =  info['exchange'],
                    market =  info['market'],
                    total_assets =  info['total_assets']
                    )
                session.add(etf_symbol)
                session.commit()
                print(f"Al 7amdu Lillah, ETF : {symbol} updated !!!!!!")

def add_indices():
    indices = fd.select_indices()
    
    for symbol,info in indices.items():
        with Session(engine) as session:
            if symbol != '':
                index_symbol = Indices(
                    symbol = symbol,
                    short_name =  info['short_name'],
                    currency =  info['currency'],
                    market =  info['market'],
                    exchange = info['exchange'],
                    exchange_timezone =  info['exchange timezone']
                    )
                session.add(index_symbol)
                session.commit()
                print(f"Al 7amdu Lillah, Index : {symbol} updated !!!!!!")


def main():
    create_db_and_tables()
    #add_currencies()
    #add_countries()
    #add_currency_countries()
    #add_stock_countries()
    add_companies_xcas()
    add_etfs()
    add_indices()
    
if __name__ == "__main__":
    main()