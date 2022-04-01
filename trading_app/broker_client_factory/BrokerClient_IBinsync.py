#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
There is a risk of loss when trading stocks, futures, forex, options and other
financial instruments. Please trade with capital you can afford to
lose. Past performance is not necessarily indicative of future results.
Nothing in this computer program/code is intended to be a recommendation, explicitly or implicitly, and/or
solicitation to buy or sell any stocks or futures or options or any securities/financial instruments.
All information and computer programs provided here is for education and
entertainment purpose only; accuracy and thoroughness cannot be guaranteed.
Readers/users are solely responsible for how to use these information and
are solely responsible any consequences of using these information.

If you have any questions, please send email to IBridgePy@gmail.com
All rights reserved.
"""
import time

from IBridgePy.IbridgepyTools import extract_contractDetails
from IBridgePy.constants import BrokerClientName
from broker_client_factory.BrokerClientDefs import ReqContractDetails
from broker_client_factory.BrokerClient_IB import ClientIB


# noinspection PyAbstractClass
class IBinsync(ClientIB):
    # !!!
    # DO NOT implement __init___ here. It will override IBCpp.__init__ and cause many errors
    @property
    def name(self):
        return BrokerClientName.IBinsync

    def _check_connectivity_reconn_if_needed(self):
        if not self.isConnectedWrapper():
            time.sleep(0.5)  # TWS needs a little bit time to clean up the previous connection. If no sleep here, errorCode 326 Unable to connect as the client id is already in use. Retry with a unique client id.
            self.connectWrapper()

    def reqPositionsWrapper(self):
        self._check_connectivity_reconn_if_needed()
        self.reqPositions()

    def reqCurrentTimeWrapper(self):
        self._check_connectivity_reconn_if_needed()
        self.reqCurrentTime()

    def reqAllOpenOrdersWrapper(self):
        self._check_connectivity_reconn_if_needed()
        self.reqAllOpenOrders()

    def reqOneOrderWrapper(self, ibpyOrderId):
        # This is not an IB native method. It is customized for Web Api based brokers. IBinsync works as same as Web Api broker
        # so that this method is needed. Invoke reqAllOpenOrdersWrapper() instead of reqOneOrder for IBinsync
        self.reqAllOpenOrdersWrapper()

    def reqAccountUpdatesWrapper(self, subscribe, accountCode):
        self._check_connectivity_reconn_if_needed()
        self.reqAccountUpdates(subscribe, accountCode)

    def reqAccountSummaryWrapper(self, reqId, group, tag):
        self._check_connectivity_reconn_if_needed()
        self.reqAccountSummary(reqId, group, tag)

    def reqHistoricalDataWrapper(self, reqId, contract, endTime, goBack, barSize, whatToShow, useRTH, formatDate):
        # print(__name__ + '::reqHistoricalDataWrapper', endTime, goBack, barSize, whatToShow, useRTH, formatDate)
        self._check_connectivity_reconn_if_needed()
        self.reqHistoricalData(reqId, contract, endTime, goBack, barSize, whatToShow, useRTH, formatDate)

    def reqMktDataWrapper(self, reqId, contract, genericTickList, snapshot):
        self._check_connectivity_reconn_if_needed()
        self.reqMktData(reqId, contract, genericTickList, snapshot)

    def cancelMktDataWrapper(self, reqId):
        self._check_connectivity_reconn_if_needed()
        self.cancelMktData(reqId)

    def reqRealTimeBarsWrapper(self, reqId, contract, barSize, whatToShow, useRTH):
        self._check_connectivity_reconn_if_needed()
        self.reqRealTimeBars(reqId, contract, barSize, whatToShow, useRTH)

    def modifyOrderWrapper(self, contract, order, ibpyRequest):
        self._check_connectivity_reconn_if_needed()
        self.placeOrderWrapper(contract, order, ibpyRequest)

    def placeOrderWrapper(self, contract, ibcppOrder, ibpyRequest):
        self._check_connectivity_reconn_if_needed()
        orderId = ibcppOrder.orderId
        if isinstance(orderId, int) and orderId != 0:
            self._log.debug(__name__ + '::placeOrderWrapper: orderId=%s' % (ibcppOrder.orderId,))
            int_orderId = ibcppOrder.orderId
        else:
            int_orderId = self.use_next_id()
            ibcppOrder.orderId = int_orderId
            self._log.debug(__name__ + '::placeOrderWrapper: reqIds and then orderId=%s' % (int_orderId,))
        self._placeOrderHelper(int_orderId, ibpyRequest, contract, ibcppOrder)

    def reqContractDetailsWrapper(self, reqId, contract):
        self._check_connectivity_reconn_if_needed()
        self.reqContractDetails(reqId, contract)

    def calculateImpliedVolatilityWrapper(self, reqId, contract, optionPrice, underPrice):
        self._check_connectivity_reconn_if_needed()
        self.calculateImpliedVolatility(reqId, contract, optionPrice, underPrice)

    def reqScannerSubscriptionWrapper(self, reqId, subscription):
        self._check_connectivity_reconn_if_needed()
        self.reqScannerSubscription(reqId, subscription)

    def cancelScannerSubscriptionWrapper(self, tickerId):
        self._check_connectivity_reconn_if_needed()
        self.cancelScannerSubscription(tickerId)

    def cancelOrderWrapper(self, ibpyOrderId):
        self._check_connectivity_reconn_if_needed()
        ibOrderId = self._idConverter.fromBrokerToIB(ibpyOrderId)
        self._log.info('cancelOrder is sent to %s ibpyOrderId=%s' % (self.name, ibpyOrderId))
        self.cancelOrder(ibOrderId)

    def reqScannerParametersWrapper(self):
        self._check_connectivity_reconn_if_needed()
        self.reqScannerParameters()

    def processMessagesWrapper(self, dummy):
        # self._log.notset(__name__ + '::processMessagesWrapper: dummyTimeNow=%s' % (dummy,))
        self.processMessages()  # IBCpp function
        return True

    def get_contract_details(self, security, field):
        """
        Implement this method in brokerClient so that add_exchange_to_security can use it in brokerClient
        :param security:
        :param field:
        :return:
        """
        self._log.debug(__name__ + '::get_contract_details: security=%s field=%s' % (security, field))
        reqIdList = self.request_data(ReqContractDetails(security))
        result = self.get_submit_requests_result(reqIdList[0])  # return a dataFrame
        ans = extract_contractDetails(result, field)
        # print(ans)
        return ans
