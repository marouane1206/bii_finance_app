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
from sys import exit

from IBridgePy.IbridgepyTools import extract_contractDetails, search_security_in_file
from IBridgePy.constants import LiveBacktest, SymbolStatus, BrokerName
from broker_client_factory.BrokerClientDefs import ReqContractDetails, ReqIds, ReqAttr
from broker_client_factory.CallBacks import CallBacks


# noinspection PyAbstractClass
from models.utils import print_IBCpp_contract, print_IBCpp_order


class ClientIB(CallBacks):
    def reqOneOrderWrapper(self, ibpyOrderId):
        raise NotImplementedError(self.name)

    def get_new_TD_refresh_token(self):
        raise NotImplementedError(self.name)

    def get_TD_access_token_expiry_in_days(self):
        raise NotImplementedError(self.name)

    # !!!
    # DO NOT implement __init___ here. It will override IBCpp.__init__ and cause many errors

    @property
    def brokerName(self):
        return BrokerName.IB

    def setup_this_client(self, log, accountCode, rootFolderPath, singleTrader, dataFromServer, timeGenerator, host, port, clientId):
        """
        this is __init__
        """
        self.setup(log, accountCode, rootFolderPath, singleTrader, dataFromServer, timeGenerator, self.name)
        # noinspection PyAttributeOutsideInit
        self.host = host
        # noinspection PyAttributeOutsideInit
        self.port = port
        # noinspection PyAttributeOutsideInit
        self.clientId = clientId

        self._log.debug(__name__ + '::setup_this_client')
        self.setRunningMode(LiveBacktest.LIVE)  # IBCpp function
        # ClientIB does not need a dataProvider

    def isConnectedWrapper(self):
        ans = self.isConnected()
        self._log.notset(__name__ + '::isConnectedWrapper: ans=%s' % (ans,))
        return ans

    def connectWrapper(self):
        self._log.debug(__name__ + '::connectWrapper')
        self.connect(self.host, int(self.port), int(self.clientId))

    def disconnectWrapper(self):
        self.disconnect()

    def reqPositionsWrapper(self):
        self.reqPositions()

    def reqCurrentTimeWrapper(self):
        self.reqCurrentTime()

    def reqAllOpenOrdersWrapper(self):
        self.reqAllOpenOrders()

    def reqAccountUpdatesWrapper(self, subscribe, accountCode):
        self.reqAccountUpdates(subscribe, accountCode)

    def reqAccountSummaryWrapper(self, reqId, group, tag):
        self.reqAccountSummary(reqId, group, tag)

    def reqIdsWrapper(self):
        self.reqIds(0)

    def reqHeartBeatsWrapper(self):
        self.reqHeartBeats()

    def reqHistoricalDataWrapper(self, reqId, contract, endTime, goBack, barSize, whatToShow, useRTH, formatDate):
        # print(__name__ + '::reqHistoricalDataWrapper', endTime, goBack, barSize, whatToShow, useRTH, formatDate)
        self.connectWrapper()
        self.reqHistoricalData(reqId, contract, endTime, goBack, barSize, whatToShow, useRTH, formatDate)

    def reqMktDataWrapper(self, reqId, contract, genericTickList, snapshot):
        self.reqMktData(reqId, contract, genericTickList, snapshot)

    def cancelMktDataWrapper(self, reqId):
        self.cancelMktData(reqId)

    def reqRealTimeBarsWrapper(self, reqId, contract, barSize, whatToShow, useRTH):
        self.reqRealTimeBars(reqId, contract, barSize, whatToShow, useRTH)

    def modifyOrderWrapper(self, contract, order, ibpyRequest):
        self.placeOrderWrapper(contract, order, ibpyRequest)

    def placeOrderWrapper(self, contract, ibcppOrder, ibpyRequest):
        raise NotImplementedError(self.name)

    def _placeOrderHelper(self, int_orderId, ibpyRequest, contract, ibcppOrder):
        ibpyOrderId = self._idConverter.fromIBtoBroker(int_orderId)

        # Set for ending flat.
        # Otherwise, the following line in broker_client_factory::CallBacks::orderStatus will not be able to find a reqId
        # reqId = self.activeRequests.find_reqId_by_int_orderId(int_orderId)
        ibpyRequest.param['int_orderId'] = int_orderId

        # Register ibpyOrderId in SingleTrader so that it can search accountCode by incoming int_orderId
        self._singleTrader.set_from_send_req_to_server(self.name, ibcppOrder.account, ibpyOrderId)

        # IBCpp function
        self.placeOrder(int_orderId, contract, ibcppOrder)
        self._log.debug(__name__ + '::placeOrderWrapper: int_orderId=%s contract=%s ibcppOrder=%s' % (int_orderId, print_IBCpp_contract(contract), print_IBCpp_order(ibcppOrder)))

        # Only IB order may not follow up.
        # If do not follow up on order, just set ending flag and assign ibpyOrderId here.
        if not ibpyRequest.followUp:
            ibpyRequest.returnedResult = ibpyOrderId
            ibpyRequest.status = ReqAttr.Status.COMPLETED

        # !!! DO NOT DELETE
        # I was trying to calculate availableFunds after placing limit order, Market Order but IB does not reduce availableFunds
        # after limit order is placed at least for paper account.
        # After market order is executed, updateAccountValue was immediately called back so that there is not need to handle availableFunds
        # So, the user should be responsible to manage availableFunds during IBridgePy session.
        # IB will not callback updateAccountValue immediately after placeOrder
        # http://www.ibridgepy.com/knowledge-base/#Q_What_functions_will_be_called_back_from_IB_server_and_what_is_the_sequence_of_call_backs_after_an_order_is_executed
        # To make sure the user know the rough AvailableFunds, IBridgePy has to simulate them.
        # The accurate value will be updated by IB regular updateAccountValue every 3 minutes.
        # The positionValue and portfolioValues are not simulated for live trading because the user just care about AvailableFunds to buy other contracts
        # These values will be updated by IB regular updateAccountValue every 3 minutes.
        # if ibcppOrder.orderType in [OrderType.LMT, OrderType.MKT]:
        #     currentCashValue = self.singleTrader.get_account_info(self.name, ibcppOrder.account, 'TotalCashValue')
        #     availableFunds = self.singleTrader.get_account_info(self.name, ibcppOrder.account, 'AvailableFunds')
        #     usedFunds = None
        #     if ibcppOrder.orderType == OrderType.LMT:
        #         usedFunds = ibcppOrder.totalQuantity * float(ibcppOrder.lmtPrice)
        #     elif ibcppOrder.orderType == OrderType.MKT:
        #         usedFunds = ibcppOrder.totalQuantity * self.dataFromServer.get_value(from_contract_to_security(contract), IBCpp.TickType.LAST, 'price')
        #     currentCashValue -= usedFunds
        #     availableFunds -= usedFunds
        #     self.updateAccountValue('TotalCashValue', currentCashValue, 'USD', ibcppOrder.account)
        #     self.updateAccountValue('AvailableFunds', availableFunds, 'USD', ibcppOrder.account)

    def reqContractDetailsWrapper(self, reqId, contract):
        self.reqContractDetails(reqId, contract)

    def calculateImpliedVolatilityWrapper(self, reqId, contract, optionPrice, underPrice):
        self.calculateImpliedVolatility(reqId, contract, optionPrice, underPrice)

    def reqScannerSubscriptionWrapper(self, reqId, subscription):
        self.reqScannerSubscription(reqId, subscription)

    def cancelScannerSubscriptionWrapper(self, tickerId):
        self.cancelScannerSubscription(tickerId)

    def cancelOrderWrapper(self, ibpyOrderId):
        ibOrderId = self._idConverter.fromBrokerToIB(ibpyOrderId)
        self._log.info('cancelOrder is sent to %s ibpyOrderId=%s' % (self.name, ibpyOrderId))
        self.cancelOrder(ibOrderId)

    def reqScannerParametersWrapper(self):
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

    def add_exchange_to_security(self, security):
        """
        This method has to stay here because both of brokerService and dataProvider need to use this method
        :param security:
        :return: None
        """
        self._log.debug(__name__ + '::add_exchange_to_security: security=%s' % (security.full_print(),))
        if security.symbolStatus != SymbolStatus.SUPER_SYMBOL:
            if security.exchange:
                # https://ibridgepy.com/knowledge-base/#Q_I_requested_STK_NASDAQTSLAUSD_but_saw_this_error_8220No_security_definition_found8221
                if security.exchange == 'NASDAQ':
                    security.exchange = 'ISLAND'
                return
            if security.secType == 'CASH':
                security.exchange = 'IDEALPRO'
                return
            security.exchange = 'SMART'

    def add_primaryExchange_to_security(self, security):
        """
        This method has to stay here because both of brokerService and dataProvider need to use this method
        :param security:
        :return: None
        """
        self._log.debug(__name__ + '::add_primaryExchange_to_security: security=%s' % (security.full_print(),))
        if security.primaryExchange:
            return
        if security.secType == 'CASH':
            security.primaryExchange = 'IDEALPRO'
            return
        ans = search_security_in_file(self._security_info, security.secType, security.symbol, security.currency, 'primaryExchange')
        if ans is None:
            if self.getAuthedVersion() <= 1:
                self._log.error(r'The combination of (%s %s %s) does not exist in IBridgePy/security_info.csv' % (security.secType, security.symbol, security.currency))
                self._log.error('Hint 1: Please refer to this YouTube tutorial about security_info.csv https://youtu.be/xyjKQPfyNRo')
                self._log.error('Hint 2: For Premium users, IBridgePy will search it automatically. Please refer to Premium features https://ibridgepy.com/features-of-ibridgepy/')
                exit()
            else:
                ans = self.get_contract_details(security, 'primaryExchange')['primaryExchange']
                self._log.debug(__name__ + '::add_primaryExchange_to_security: Found from IB server ans=%s' % (ans,))
        else:
            self._log.debug(__name__ + '::add_primaryExchange_to_security: Found from security_info.csv ans=%s' % (ans,))
        if ans:
            security.primaryExchange = ans
        else:
            self._log.error(__name__ + '::add_primaryExchange_to_security: EXIT, security=%s cannot get primaryExchange from server.' % (security.full_print(),))
            exit()

    def use_next_id(self):
        self._log.debug(__name__ + '::use_next_id: name=%s' % (self.name,))
        # It is possible that users run multiple IBridgePy instances at the same time.
        # In that case, reqIds() only at the beginning won't work because multiple IBridgePy instances can consume ids
        # at the same time. Therefore, explicitly reqIds() here to get a refresh id.
        self.request_data(ReqIds())
        return self._nextId.useOne()
