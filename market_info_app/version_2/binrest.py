import requests
# import json
import csv, time



kline_intervals = ('1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M')

BASE_URL = "https://api.binance.com/api/v3/"


class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"
        super().__init__(message)


def timediff():
    PATH =  'time'
    params = None
    timestamp = int(time.time() * 1000)
    url = BASE_URL + PATH
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        print(f"diff={timestamp - data['serverTime']}ms")
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())


def all_tickers():
    endpt = BASE_URL + "ticker/price"
    r = requests.get(endpt)
    result = r.json()
    print(result, len(result))


def kline(symbol = 'BTCUSDT', interval='1m', starttime=None, endtime=None, limit=None):
    PATH = 'klines'
    endpt = BASE_URL + PATH

    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': starttime,
        'endTime': endtime,
        'limit': limit}
    
    r = requests.get(endpt, params=params)
    result = r.json()
    return result,r 
    # if r.status_code == 200:
    #     print(json.dumps(r.json(), indent=2))
    # else:
    #     raise BinanceException(status_code=r.status_code, data=r.json())


def main():
    candles, r = kline(interval='1d', limit=10000)
    print(candles, len(candles), type(candles), r.status_code)
    # csvfile = open('btc_day.csv','w',newline='')
    # candlewriter = csv.writer(csvfile, delimiter=',')
    # for candlestick in candles:
    #     print(candlestick)
    #     candlewriter.writerow(candlestick)
    timediff()


if __name__ == "__main__":
    main()