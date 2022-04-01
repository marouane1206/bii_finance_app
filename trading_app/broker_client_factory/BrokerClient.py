# coding=utf-8
import datetime as dt
import os

import pandas as pd

# noinspection PyUnresolvedReferences
from IBridgePy import IBCpp
from IBridgePy.IbridgepyTools import read_hash_config
from IBridgePy.quantopian import from_security_to_contract
from broker_client_factory.BrokerClientDefs import ReqAttr, ActiveRequestBatch, ReqHeartBeats
from broker_client_factory.broker_client_utils import Converter
from models.utils import print_IBCpp_contract, print_IBCpp_order


class CollectionRealTimePriceRequested(object):
    def __init__(self):
        self.realTimePriceRequestById = {}

        # keyed by str_security that include exchange and primaryExchange, value = reqId
        # Use str_security to deduplicate
        self.realTimePriceRequestByStrSecurity = {}

    def addReqIdAndStrSecurity(self, reqId, str_security):
        self.realTimePriceRequestById[reqId] = str_security
        self.realTimePriceRequestByStrSecurity[str_security] = reqId

    def deleteReqIdAndStrSecurity(self, reqId, str_security):
        del self.realTimePriceRequestById[reqId]
        del self.realTimePriceRequestByStrSecurity[str_security]

    def findByReqId(self, reqId):
        return self.realTimePriceRequestById[reqId]

    def findByStrSecurity(self, str_security):
        return self.realTimePriceRequestByStrSecurity[str_security]

    def getAllStrSecurity(self):
        """
        Get all securities that have requested real time prices
        :return: a list of str_security
        """
        return self.realTimePriceRequestByStrSecurity

    def checkIfRequestedByStrSecurity(self, str_security):
        return str_security in self.realTimePriceRequestByStrSecurity


class Uuid(object):
    def __init__(self):
        self.uuid = 0

    def setUuid(self, value):
        self.uuid = value

    def useOne(self):
        ans = self.uuid
        self.uuid += 1
        return ans


class BrokerClientBase(IBCpp.IBClient):
    """
    !!!! Do not implement __init__, otherwise it will supersede IBCpp.__init__ and cause errors

    BrokerClientBase lists all of interface functions for outside.
        use_next_id --- used for placing combination orders TODO: can be removed by sharing nextId with brokerService
    singleTrader and dataFromServer are updated by BrokerClient and they are shared with BrokerService.
    """
    versionNumber = '16.2.2'

    def __str__(self):
        return '{name=%s id=%s accountCode=%s dataProvider=%s}' % (self.name, id(self), self._accountCode, self._dataProvider)

    # !!!! Do not implement __init__, otherwise it will supersede IBCpp.__init__ and cause errors
    # noinspection PyAttributeOutsideInit
    def setup(self, log, accountCode, rootFolderPath, singleTrader, dataFromServer, timeGenerator, brokerClientName):
        # these are needed to construct an instance
        self._log = log
        self._accountCode = accountCode

        # models::Traders::Trader
        # It is a decouple tool between BrokerService and BrokerClient
        # It stores trader's account related info, such as positions, orders, accountValues
        self._singleTrader = singleTrader

        # models::Data::Data
        # It is a decouple tool between BrokerService and BrokerClient
        # It stores non-account related dataFromServer
        self._dataFromServer = dataFromServer
        self._timeGenerator = timeGenerator

        self._nextId = Uuid()  # nextValidId, all request will use the same series

        # record all realTimeRequests to avoid repeat calls
        # Support findByReqId, findByStrSecurity, getAllStrSecurity
        self._realTimePriceRequestedList = CollectionRealTimePriceRequested()

        path = os.path.join(rootFolderPath, 'IBridgePy', 'hash.conf')
        self.setHashConfig(read_hash_config(path))  # IBCpp function

        # IBCpp function
        # For single account, just input accountCode
        # For multi account, input "All" --- TODO: need to verify it 20181114
        # Must happen after setHashConfig is invoked.
        if isinstance(accountCode, str):
            self.setAuthedAcctCode(self._accountCode)  # IBCpp function
        else:
            self.setAuthedAcctCode('All')  # IBCpp function

        # Other brokers use string orderId, IB use integer orderId.
        # In IBridgePy, broker_client_factory::broker_client_utils::Converter is used to convert between them
        self._idConverter = Converter(brokerClientName, createrOfIBValue=self._nextId)  #

        # read in IBridgePy/security_info.csv
        self._security_info = pd.read_csv(os.path.join(rootFolderPath, 'IBridgePy', 'security_info.csv'))
        self._log.debug(__name__ + '::__init__')

        # noinspection PyAttributeOutsideInit
        self._dataProvider = None  # only brokerClient.localFile needs a dataProvider here.

        # False = backtesting; True = work as a dataProviderClient, self._dataProvider is responsible to provide data/hist
        # noinspection PyAttributeOutsideInit
        self._asDataProviderClient = False

        # TODO: these values are not used anywhere 20200928
        self._connectionGatewayToServer = True
        self._connectionMarketDataFarm = True
        self._connectionHistDataFarm = True

        # When each request is processed in broker_client_factory::RequestImpl::_send_req_to_server, each request is copied
        # to allRequests for recording
        self._allRequests = {}

        # broker_client_factory::BrokerClientDefs::ActiveRequestBatch.
        # Only create a new instance in BrokerClient::request_data
        # When each request is processed in broker_client_factory::RequestImpl::_send_req_to_server, each request is copied
        # to allRequests for recording
        self._activeRequests = None

    def getDataProvider(self):
        return self._dataProvider

    def setAsDataProviderClient(self):
        # noinspection PyAttributeOutsideInit
        self._asDataProviderClient = True

    def get_authed_expiry(self):
        """

        :return: int, number of days of IBridgePy passcode to expiry
        """
        authedLevel = self.getAuthedVersion()  # IBCpp function
        expiry = self.getExpiry(authedLevel)  # string = '20201024'
        return (dt.datetime.strptime(expiry, "%Y%m%d") - dt.datetime.now()).days  # string -> dt.datetime

    def get_TD_access_token_expiry_in_days(self):
        raise NotImplementedError(self.name)

    def get_new_TD_refresh_token(self):
        raise NotImplementedError(self.name)

    def get_heart_beats(self):
        self.request_data(ReqHeartBeats())

    def processMessagesWrapper(self, timeNow):
        raise NotImplementedError(self.name)

    def isConnectedWrapper(self):
        raise NotImplementedError(self.name)

    def connectWrapper(self):
        raise NotImplementedError(self.name)

    def disconnectWrapper(self):
        raise NotImplementedError(self.name)

    def reqPositionsWrapper(self):
        raise NotImplementedError(self.name)

    def reqCurrentTimeWrapper(self):
        raise NotImplementedError(self.name)

    def reqAllOpenOrdersWrapper(self):
        raise NotImplementedError(self.name)

    def reqOneOrderWrapper(self, ibpyOrderId):
        raise NotImplementedError(self.name)

    def reqAccountUpdatesWrapper(self, subscribe, accountCode):
        raise NotImplementedError(self.name)

    def reqAccountSummaryWrapper(self, reqId, group, tag):
        raise NotImplementedError(self.name)

    def reqIdsWrapper(self):
        raise NotImplementedError(self.name)

    def reqHeartBeatsWrapper(self):
        raise NotImplementedError(self.name)

    def reqHistoricalDataWrapper(self, reqId, contract, endTime, goBack, barSize, whatToShow, useRTH, formatDate):
        raise NotImplementedError(self.name)

    def reqMktDataWrapper(self, reqId, contract, genericTickList, snapshot):
        raise NotImplementedError(self.name)

    def cancelMktDataWrapper(self, reqId):
        raise NotImplementedError(self.name)

    def reqRealTimeBarsWrapper(self, reqId, contract, barSize, whatToShow, useRTH):
        raise NotImplementedError(self.name)

    def placeOrderWrapper(self, contract, order, ibpyRequest):
        raise NotImplementedError(self.name)

    def modifyOrderWrapper(self, contract, order, ibpyRequest):
        raise NotImplementedError(self.name)

    def reqContractDetailsWrapper(self, reqId, contract):
        raise NotImplementedError(self.name)

    def calculateImpliedVolatilityWrapper(self, reqId, contract, optionPrice, underPrice):
        raise NotImplementedError(self.name)

    def reqScannerSubscriptionWrapper(self, reqId, subscription):
        raise NotImplementedError(self.name)

    def cancelScannerSubscriptionWrapper(self, tickerId):
        raise NotImplementedError(self.name)

    def cancelOrderWrapper(self, ibpyOrderId):
        raise NotImplementedError(self.name)

    def reqScannerParametersWrapper(self):
        raise NotImplementedError(self.name)

    def get_submit_requests_result(self, reqId):
        return self._allRequests[reqId].returnedResult

    def use_next_id(self):
        return self._nextId.useOne()

    def get_datetime(self):
        return self._timeGenerator.get_current_time()

    def check_if_real_time_price_requested(self, security):
        self._log.notset(__name__ + '::check_if_real_time_price_requested: security=%s' % (str(security),))
        return self._realTimePriceRequestedList.checkIfRequestedByStrSecurity(security.full_print())

    def request_data(self, *args):
        """
        !!! return a list of reqId, reqId != orderId
        TODO: do not repeat 20190705
        input:
        request_data(
                     ReqPositions(),
                     ReqAccountUpdates(True, 'test_me'),
                     ReqAccountSummary(),
                     ReqIds(),
                     ReqHistoricalData(self.sybmol('SPY'),
                                               '1 day', '10 D', dt.datetime.now()),
                     ReqMktData(self.sybmol('SPY')),
                     ReqRealTimeBars(self.symbol('SPY')),
                     ReqContractDetails(self.symbol('SPY')),
                     CalculateImpliedVolatility(self.symbol('SPY'), 99.9, 11.1),
                     ReqAllOpenOrders(),
                     CancelMktData(1),
                     ReqCurrentTime())
        """
        self._log.notset(__name__ + '::request_data')

        # reqId and orderId are filled here using self.nextId
        # noinspection PyAttributeOutsideInit
        self._activeRequests = ActiveRequestBatch(args, self._nextId)

        # send request to IB server
        self._send_req_to_server(self._activeRequests)

        # continuously check if all requestRecord have received responses until default 30 seconds
        while not self._activeRequests.check_all_completed():  # default 30 second is checked in check_all_completed
            failedReqIds = self._activeRequests.find_failed_requests()
            if len(failedReqIds) >= 1:
                self._log.error(__name__ + '::request_data: EXIT, the following requestRecord failed')
                for reqId in failedReqIds:
                    request = self._activeRequests.get_by_reqId_otherwise_exit(reqId)
                    self._log.error(str(request))
                    if request.reqType == 'reqHistoricalData':
                        if request.status == ReqAttr.Status.STARTED:
                            self._log.error(r'Hint 1: IBridgePy waits for broker responses for 30 seconds default and errors out if completed responses have not been recorded. Consider to increase waitForFeedbackInSeconds. Refer to https://ibridgepy.com/ibridgepy-documentation/#request_historical_data')
                        else:
                            if not self._connectionHistDataFarm:
                                self._log.error(r'Hint: Connection to Hist Data Farm is broken.')
                            else:
                                self._log.error(r'Hint 1: The most common reason is that broker historical data service is not available at this moment, especially when US market is closed. Try the request later.')
                                self._log.error(r'Hint 2: The less common reason is that broker server does not response if the request violates broker rules about bar size. Refer to http://interactivebrokers.github.io/tws-api/historical_limitations.html#non-available_hd')
                raise RuntimeError('%s server did not response to the request at all. Maybe the market is closed? Consider trying it later.' % (self.name, ))
            self.processMessagesWrapper(None)
        self._log.debug(__name__ + '::request_data: All responses are received')
        self._log.debug(__name__ + '::request_data: COMPLETED')
        return self._activeRequests.get_request_ids()  # return a list of reqId

    def _send_req_to_server(self, activeRequests):
        """
        pandas dataFrame: reqData
        All requests are defined in broker_client_factory::BrokerClientDefs
        """
        self._log.debug(__name__ + '::_send_req_to_server: brokerClient=%s' % (self,))

        for reqId in activeRequests.get_request_ids():
            aRequest = activeRequests.get_by_reqId_otherwise_exit(reqId)
            self._allRequests[reqId] = aRequest  # move to allRequest which stores all requests
            aRequest.status = ReqAttr.Status.SUBMITTED
            reqType = aRequest.reqType
            param = aRequest.param
            self._log.debug('%s' % (aRequest,))

            if reqType == 'reqPositions':
                self.reqPositionsWrapper()

            elif reqType == 'reqConnect':
                ans = self.isConnectedWrapper()
                if ans:
                    aRequest.status = ReqAttr.Status.COMPLETED
                else:
                    ans = self.connectWrapper()
                    if ans:
                        aRequest.status = ReqAttr.Status.COMPLETED

            elif reqType == 'reqCurrentTime':
                self.reqCurrentTimeWrapper()

            elif reqType == 'reqAllOpenOrders':
                self.reqAllOpenOrdersWrapper()

            elif reqType == 'reqOneOrder':
                ibpyOrderId = param['orderId']
                self.reqOneOrderWrapper(ibpyOrderId)

            elif reqType == 'reqAccountUpdates':
                accountCode = param['accountCode']
                subscribe = param['subscribe']
                self.reqAccountUpdatesWrapper(subscribe, accountCode)  # Request to update account info

            elif reqType == 'reqAccountSummary':
                group = param['group']
                tag = param['tag']
                self.reqAccountSummaryWrapper(reqId, group, tag)

            elif reqType == 'reqIds':
                self.reqIdsWrapper()

            elif reqType == 'reqHeartBeats':
                self.reqHeartBeatsWrapper()

            elif reqType == 'reqHistoricalData':
                security = param['security']
                endTime = param['endTime']
                goBack = param['goBack']
                barSize = param['barSize']
                whatToShow = param['whatToShow']
                useRTH = param['useRTH']
                formatDate = 2  # param['formatDate'] Send epoch to IB server all the time. It is easier to handle
                self.reqHistoricalDataWrapper(reqId,
                                              from_security_to_contract(security),
                                              endTime,
                                              goBack,
                                              barSize,
                                              whatToShow,
                                              useRTH,
                                              formatDate)

            elif reqType == 'reqMktData':
                security = param['security']
                genericTickList = param['genericTickList']
                snapshot = param['snapshot']

                # put security and reqID in dictionary for fast access
                # it is keyed by both security and reqId
                self._realTimePriceRequestedList.addReqIdAndStrSecurity(reqId, security.full_print())

                self.reqMktDataWrapper(reqId, from_security_to_contract(security),
                                       genericTickList, snapshot)  # Send market data request to IB server

            elif reqType == 'cancelMktData':
                security = param['security']
                reqId = self._realTimePriceRequestedList.findByStrSecurity(security.full_print())
                self.cancelMktDataWrapper(reqId)
                self._realTimePriceRequestedList.deleteReqIdAndStrSecurity(reqId, security.full_print())

            elif reqType == 'reqRealTimeBars':
                security = param['security']
                barSize = param['barSize']
                whatToShow = param['whatToShow']
                useRTH = param['useRTH']
                self._realTimePriceRequestedList.addReqIdAndStrSecurity(reqId, security.full_print())
                self.reqRealTimeBarsWrapper(reqId,
                                            from_security_to_contract(security),
                                            barSize, whatToShow, useRTH)  # Send market dataFromServer request to IB server

            elif reqType == 'placeOrder':
                """
                Ending label is IBCpp::callBacks::orderStatus
                """
                contract = param['contract']
                order = param['order']
                self.placeOrderWrapper(contract, order, aRequest)

                # When the order is placed, IB will callback orderStatus
                # In broker_client_factory::CallBack::orderStatus, IBridgePy, set ending flag for this request and assign ibpyOrderId
                # self.activeRequests.get_by_reqId_otherwise_exit(reqId).returnedResult = str_ibpyOrderId
                # self.activeRequests.get_by_reqId_otherwise_exit(reqId).status = ReqAttr.Status.COMPLETED

            elif reqType == 'modifyOrder':
                """
                Ending label is IBCpp::callBacks::orderStatus
                """
                ibpyOrderId = param['ibpyOrderId']
                contract = param['contract']
                order = param['order']

                int_orderId = order.orderId
                self._idConverter.verifyRelationship(int_orderId, ibpyOrderId)
                self._log.info('ModifyOrder ibpyOrderId=%s security=%s order=%s' % (ibpyOrderId, print_IBCpp_contract(contract), print_IBCpp_order(order)))
                self.modifyOrderWrapper(contract, order, aRequest)

            elif reqType == 'reqContractDetails':
                security = param['security']
                self.reqContractDetailsWrapper(reqId, from_security_to_contract(security))

            elif reqType == 'calculateImpliedVolatility':
                security = param['security']
                optionPrice = float(param['optionPrice'])
                underPrice = float(param['underPrice'])

                # put security and reqID in dictionary for fast access
                # it is keyed by both security and reqId
                self._realTimePriceRequestedList.addReqIdAndStrSecurity(reqId, security.full_print())

                self.calculateImpliedVolatilityWrapper(reqId,
                                                       from_security_to_contract(security),
                                                       optionPrice,
                                                       underPrice)

            elif reqType == 'reqScannerSubscription':
                subscription = param['subscription']
                self.reqScannerSubscriptionWrapper(reqId, subscription)

                # Need to upgrade IBCpp
                # tagValueList = self.end_check_list.loc[idx, 'reqData'].param['tagValueList']
                # self.reqScannerSubscription(reqId, subscription, tagValueList)
                # self._log.debug(__name__ + '::_send_req_to_server:reqScannerSubscription:'
                #               + ' subscription=' + subscription.full_print() + ' tagValueList=' + str(tagValueList))

            elif reqType == 'cancelScannerSubscription':
                tickerId = param['tickerId']
                self.cancelScannerSubscriptionWrapper(tickerId)

            elif reqType == 'cancelOrder':
                """
                Ending label is IBCpp::callBacks::error: errorCode = 10148
                Do not use orderStatus callback to follow up on cancelOrder request because the status can be either Canceled Or PendingCancel
                """
                ibpyOrderId = param['ibpyOrderId']
                int_orderId = self._idConverter.fromBrokerToIB(ibpyOrderId)
                param['int_orderId'] = int_orderId
                self.cancelOrderWrapper(ibpyOrderId)

            elif reqType == 'reqScannerParameters':
                self.reqScannerParametersWrapper()
            else:
                self._log.error(__name__ + '::_send_req_to_server: EXIT, cannot handle reqType=%s' % (reqType,))
                self.end()

    def add_exchange_to_security(self, security):
        """
        Stay in brokerClient so that it can be replaced by fetching from IB server.
        :param security:
        :return:
        """
        raise NotImplementedError(self.name)
        # self._log.debug(__name__ + '::add_exchange_to_security: security=%s' % (security.full_print(),))
        # if not security.exchange:
        #     security.exchange = search_security_in_file(self._security_info, security.secType, security.symbol,
        #                                                 security.currency, 'exchange')

    def add_primaryExchange_to_security(self, security):
        """
        Stay in brokerClient so that it can be replaced by fetching from IB server.
        :param security:
        :return:
        """
        raise NotImplementedError(self.name)
        # self._log.debug(__name__ + '::add_primaryExchange_to_security: security=%s' % (security.full_print(),))
        # if not security.primaryExchange:
        #     security.primaryExchange = search_security_in_file(self._security_info, security.secType, security.symbol,
        #                                                        security.currency, 'primaryExchange')

    def append_security_info(self, security):
        """
        Add security into security_info mini db so that user don't need to manully add them in security_info.csv
        :param security:
        :return:
        """
        # noinspection PyAttributeOutsideInit
        self._security_info = self._security_info.append(pd.Series({'symbol': security.symbol,
                                                                    'exchange': security.exchange,
                                                                    'primaryExchange': security.primaryExchange}),
                                                         ignore_index=True)
