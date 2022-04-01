# -*- coding: utf-8 -*-
"""
All rights reserved.
@author: IBridgePy@gmail.com
"""
from IBridgePy.constants import DataProviderName, LogLevel, BrokerClientName


# Put here to avoid cyclic import
def _invoke_log(userConfig, caller, message):
    if userConfig.projectConfig.logLevel in [LogLevel.DEBUG, LogLevel.NOTSET]:
        print(__name__ + '::%s:%s' % (caller, message))


def get_dataProvider(userConfig):
    name = userConfig.projectConfig.dataProviderName
    if name == DataProviderName.LOCAL_FILE:
        from .dataProvider_localFile import LocalFile
        t = LocalFile(userConfig.log, None, userConfig.projectConfig.useColumnNameWhenSimulatedByDailyBar)
    elif name == DataProviderName.RANDOM:
        from .dataProvider_random import RandomDataProvider
        t = RandomDataProvider(userConfig.log, None)
    elif name == DataProviderName.IB:
        from .dataProvider_IB import IB
        t = IB(userConfig.log, userConfig.brokerClientFactory.get_brokerClient_by_name(BrokerClientName.IB, userConfig), userConfig.projectConfig.useColumnNameWhenSimulatedByDailyBar)
    elif name == DataProviderName.TD:
        from .dataProvider_TD import TD
        t = TD(userConfig.log, userConfig.brokerClientFactory.get_brokerClient_by_name(BrokerClientName.TD, userConfig), userConfig.projectConfig.useColumnNameWhenSimulatedByDailyBar)
    elif name == DataProviderName.IBRIDGEPY:
        from .dataProvider_IBPY import IBPY
        t = IBPY(userConfig.log, userConfig.emailClientConfig.IBRIDGEPY_EMAIL_CLIENT['apiKey'], userConfig.projectConfig.useColumnNameWhenSimulatedByDailyBar)
    else:
        raise RuntimeError(__name__, 'cannot handle dataProviderName=%s' % (name,))
    if t.name not in [DataProviderName.RANDOM, DataProviderName.LOCAL_FILE, DataProviderName.IBRIDGEPY] and t.name != t.get_dataProviderClient().name:
        if t.name == DataProviderName.IB:
            if t.get_dataProviderClient().name != BrokerClientName.IBinsync:
                raise RuntimeError('dataProviderName=%s dataProviderClientName=%s !They are not same!' % (t.name, t.get_dataProviderClient().name))
        else:
            raise RuntimeError('dataProviderName=%s dataProviderClientName=%s !They are not same!' % (t.name, t.get_dataProviderClient().name))

    _invoke_log(userConfig, 'get_dataProvider', 'created dataProvider=%s' % (t,))
    return t
