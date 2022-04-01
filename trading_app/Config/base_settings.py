# coding=utf-8
import os

import pytz

from IBridgePy.constants import TimeGeneratorType, LogLevel, LiveBacktest, TraderRunMode

DATABASE = {
    'DB_HOST': os.environ.get('DB_HOST'),
    'DB_USERNAME': os.environ.get('DB_USERNAME'),
    'DB_PASSWORD':os.environ.get('DB_PASSWORD'),
    'DB_NAME': os.environ.get('DB_NAME')
}

MARKET_MANAGER = {
    'baseFreqOfProcessMessage': 1,
    'marketName': None,
    'beforeTradeStartHour': None,
    'beforeTradeStartMinute': None
}

REPEATER = {
    'slowdownInSecond': 0.5
}

TIME_GENERATOR = {
    'timeGeneratorType': TimeGeneratorType.LIVE,  # Live, Auto, Custom
    'startingTime': None,
    'endingTime': None,
    'freq': None,
    'custom': []
}

BACKTESTER = {
    'initPortfolioValue': 100000.0
}

PROJECT = {
    'accountCode': '',
    'fileName': '',
    'logLevel': LogLevel.INFO,
    'repBarFreq': None,
    'dataProviderName': None,
    'brokerServiceName': None,
    'brokerClientName': None,
    'brokerName': None,
    'sysTimeZone': pytz.timezone('US/Eastern'),
    'liveOrBacktest': LiveBacktest.LIVE,
    'rootFolderPath': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'histIngestionPlan': None,
    'runScheduledFunctionBeforeHandleData': False,  # As same as in Quantopian
    'showTimeZone': pytz.timezone('US/Eastern'),
    'useColumnNameWhenSimulatedByDailyBar': 'close',
    'autoReconnectPremium': False,
    'autoReconnectFreq': 60,
    'autoSearchPortNumber': True,
    'searchPortList': [7497, 7496, 4001, 4002]
}

TRADER = {
    'runMode': TraderRunMode.REGULAR  # run handle_data every second, not run_like_quantopian
}

BROKER_CLIENT = {
    'IB_CLIENT': {
        'accountCode': '',
        'host': '',  # config for IB client
        'port': 7496,  # config for IB client
        'clientId': 9,  # config for IB client
    },
    'TD_CLIENT': {
        'accountCode': '',
        'apiKey': '',
        'refreshToken': '',
        'refreshTokenCreatedOn': None  # the user input should be datetime.date()
    },
    'ROBINHOOD_CLIENT': {
        'accountCode': '',
        'username': '',
        'password': ''
    }
}

EMAIL_CLIENT = {
    'IBRIDGEPY_EMAIL_CLIENT': {
        'apiKey': ''
    }
}
