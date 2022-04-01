# coding=utf-8
import pytz
import datetime as dt

from IBridgePy.constants import TraderRunMode, MarketName

PROJECT = {
    'showTimeZone': pytz.timezone('US/Eastern'),
    'repBarFreq': 1,  # Positive numbers only
    'logLevel': 'INFO',  # Possible values are ERROR, INFO, DEBUG, NOTSET, refer to http://www.ibridgepy.com/ibridgepy-documentation/#step1-1-4
    'autoReconnectPremium': False,  # True: IBridgePy will automatically get reconnected to IB server when disconnect happen, such as TWW/Gateway restarts.
    'autoSearchPortNumber': True,  # True: IBridgePy will actively try to search the matched port number from searchPortList; False: IBridgePy will ONLY use settings.py -> BROKER_CLIENT -> IB_CLIENT -> port to connect.
    'searchPortList': [7496, 7497, 4001]  # Other port numbers can be added to this list if user want to use other port numbers and want to automatically search that port numbers.
}

BACKTESTER = {
    'initPortfolioValue': 100000.0  # The initial portfolio value when backtesting starts.
}


MARKET_MANAGER = {  # these settings are applied ONLY when traderRunMode == RUN_LIKE_QUANTOPIAN
    'marketName': MarketName.NYSE,
    'beforeTradeStartHour': 9,
    'beforeTradeStartMinute': 25,
}

TRADER = {
    # Refer to https://ibridgepy.com/documentation/#step1-1-3
    'runMode': TraderRunMode.REGULAR  # run handle_data every second. Possible values are REGULAR, RUN_LIKE_QUANTOPIAN, SUDO_RUN_LIKE_QUANTOPIAN and HFT
}

BROKER_CLIENT = {
    'IB_CLIENT': {
        'accountCode': '',
        'clientId': 9,
        'port': 7497
    },
    'TD_CLIENT': {
        'accountCode': '',
        'apiKey': '',  # put your apiKey here. Refer to this tutorial https://www.youtube.com/watch?v=l3qBYMN4yMs
        'refreshToken': '',  # put your refresh token here. Refer to this tutorial https://youtu.be/Ql6VnR0GIYY
        'refreshTokenCreatedOn': dt.date(2020, 5, 7)  # put the date when the refresh token was created. IBridgePy will remind you when it is about to expire.
    },
    'ROBINHOOD_CLIENT': {
        'accountCode': '',
        'username': '',  # put your Robinhood username here. It is ok to leave it as-is. Then, you will be prompted to input it in command line later.
        'password': '',  # put your Robinhood password here. It is ok to leave it as-is. Then, you will be prompted to input it in command line later.
    }
}

EMAIL_CLIENT = {
    'IBRIDGEPY_EMAIL_CLIENT': {
        'apiKey': ''  # To send out emails, please refer to this tutorial https://youtu.be/jkeos2QrkfQ
    }
}

