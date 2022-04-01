# coding=utf-8
# noinspection PyUnresolvedReferences
from IBridgePy import IBCpp
from IBridgePy.constants import BrokerServiceName, BrokerName
from broker_client_factory.BrokerClientDefs import ReqAccountUpdates, ReqScannerSubscription, CancelScannerSubscription
from broker_service_factory.BrokerService_web import WebApi


class IBinsync(WebApi):
    def get_timestamp(self, security, tickType):
        raise NotImplementedError

    def get_option_greeks(self, security, tickType, fields):
        self._log.debug(__name__ + '::get_option_greeks: security=%s tickType=%s fields=%s'
                        % (security.full_print(), str(tickType), str(fields)))
        ans = {}
        for fieldName in fields:
            ans[fieldName] = self._dataFromServer.get_value(security, tickType, fieldName)
        return ans

    def get_contract_details(self, security, field):
        self._log.debug(__name__ + '::get_contract_details: security=%s field=%s' % (security, field))
        return self._brokerClient.get_contract_details(security, field)

    @property
    def name(self):
        return BrokerServiceName.IBinsync

    @property
    def brokerName(self):
        return BrokerName.IB

    # noinspection DuplicatedCode
    def _get_account_info_one_tag(self, accountCode, tag, meta='value'):
        self._log.notset(__name__ + '::_get_account_info_one_tag: accountCode=%s tag=%s' % (accountCode, tag))
        submitted = self._submit_request_after_checking_cache(ReqAccountUpdates(True, accountCode))
        # noinspection DuplicatedCode
        ans = self._singleTrader.get_account_info(self.brokerName, accountCode, tag)
        if ans is None:
            self._log.error(__name__ + '::_get_account_info_one_tag: EXIT, no value based on accountCode=%s tag=%s' % (accountCode, tag))
            print('active accountCode is %s' % (self._singleTrader.get_all_active_accountCodes(self.name),))
            exit()
        if submitted:
            self.submit_requests(ReqAccountUpdates(False, accountCode))
        return ans

    def get_scanner_results(self, kwargs):
        #        numberOfRows=-1, instrument='', locationCode='', scanCode='', abovePrice=0.0,
        #        belowPrice=0.0, aboveVolume=0, marketCapAbove=0.0, marketCapBelow=0.0, moodyRatingAbove='',
        #        moodyRatingBelow='', spRatingAbove='', spRatingBelow='', maturityDateAbove='', maturityDateBelow='',
        #        couponRateAbove=0.0, couponRateBelow=0.0, excludeConvertible=0, averageOptionVolumeAbove=0,
        #        scannerSettingPairs='', stockTypeFilter=''
        tagList = ['numberOfRows', 'instrument', 'locationCode', 'scanCode', 'abovePrice', 'belowPrice', 'aboveVolume',
                   'marketCapAbove',
                   'marketCapBelow', 'moodyRatingAbove', 'moodyRatingBelow', 'spRatingAbove', 'spRatingBelow',
                   'maturityDateAbove',
                   'maturityDateBelow', 'couponRateAbove', 'couponRateBelow', 'excludeConvertible',
                   'averageOptionVolumeAbove',
                   'scannerSettingPairs', 'stockTypeFilter']
        subscription = IBCpp.ScannerSubscription()
        for ct in kwargs:
            if ct in tagList:
                setattr(subscription, ct, kwargs[ct])
        reqIdList = self.submit_requests(ReqScannerSubscription(subscription))
        self.submit_requests(CancelScannerSubscription(reqIdList[0]))
        return self._brokerClient.get_submit_requests_result(reqIdList[0])  # return a pandas dataFrame