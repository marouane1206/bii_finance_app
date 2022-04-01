# coding=utf-8
from IBridgePy.constants import BrokerServiceName, BrokerName
from broker_service_factory.BrokerService_web import WebApi


class Robinhood(WebApi):
    def get_timestamp(self, security, tickType):
        raise NotImplementedError

    def get_contract_details(self, security, field):
        raise NotImplementedError

    @property
    def name(self):
        return BrokerServiceName.ROBINHOOD

    @property
    def brokerName(self):
        return BrokerName.ROBINHOOD
