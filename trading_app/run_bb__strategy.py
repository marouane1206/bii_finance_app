import datetime as dt

from configuration import test_me

fileName = 'example_show_real_time_prices.py'

accountCode = 'DU228379'  # IB accountCode is needed to retrieve historical data from IB server.
dataProviderName = 'IB'  # RANDOM, IB, LOCAL_FILE, TD, ROBINHOOD, IBRIDGEPY

endTime = dt.datetime.now()

# As a demo, startTime is 10 days ago from the current time.
startTime = endTime - dt.timedelta(days=10)

test_me(fileName, globals())