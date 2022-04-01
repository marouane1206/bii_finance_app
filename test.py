from datetime import date, timedelta
from Config import DB_Params
import psycopg2
from iexfinance.refdata import get_symbols
import os
import requests
import pycountry
from hdx.location.country import Country

token = os.environ.get('IEX_TOKEN')
base_url = os.environ.get('IEX_BASE_URL')
params = {'token': token}
resp = requests.get(base_url + '/status')

#####################################################
print(date.today(), date.today()-timedelta(days=1))
########################################################
def populate_country(country):
    """ insert countries into the country table """
    conn = None
    try:
        params = DB_Params()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        sql = '''INSERT INTO country(
            country_id,
            country_alpha_3,
            country_flag,
            country_name,
            country_numeric) 
            VALUES('{}','{}','{}','{}','{}')'''.format(country_id,country_alpha_3,country_flag,country_name,country_numeric)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()       
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


currencies = list(pycountry.currencies)
for currency in currencies:
    #print (currency)
    currency_id = currency.alpha_3
    currency_name = currency.name
    currency_numeric = currency.numeric
    #print('Done')

countries = list(pycountry.countries)
for country in countries:
    #print(country.name)
    country_id = country.alpha_2
    currency_id = Country.get_currency_from_iso3(country.alpha_3)
    country_alpha_3 = country.alpha_3
    country_flag = country.flag
    country_name = country.name
    country_numeric = country.numeric 
    populate_country(country)


if __name__ == '__main__':
    connect()

