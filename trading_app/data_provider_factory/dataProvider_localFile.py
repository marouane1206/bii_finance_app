# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 23:50:16 2018

@author: IBridgePy@gmail.com
"""

import numpy as np
import pandas as pd

from IBridgePy.constants import DataProviderName
from tools.hist_converter import convert_hist_using_timestamp_to_epoch
from .data_provider_nonRandom import NonRandom


class LocalFile(NonRandom):
    @property
    def name(self):
        return DataProviderName.LOCAL_FILE

    def provide_hist_from_a_true_dataProvider(self, security, endTime, goBack, barSize, whatToShow, useRTH, formatDate):
        # Need to think about how to use this method
        raise NotImplementedError(self.name)

    def provide_real_time_price(self, security, tickType):
        # Need to think about how to use this method
        raise NotImplementedError(self.name)

    def ingest_hists(self, histIngestionPlan):
        """
        csv file must have 1st column integer as epoch, then open high low close volume
        hist index must be integer representing epoch time in seconds
        because it will be easier to server data when searching a spot time
        :param histIngestionPlan: histIngestionPlan: data_provider_factor::data_loading_plan::HistIngestionPlan
        :return:
        """
        self._ingest_hists(histIngestionPlan, self._get_hist_from_csv)
        self._histIngested = True

    @staticmethod
    def _get_hist_from_csv(plan):
        # print(__name__ + '::_get_hist_from_csv: plan=%s' % (plan,))
        hist = pd.read_csv(plan.fullFileName,
                           index_col=0,  # first column is index column
                           # parse_dates=True,  # first column should be parse to date
                           # date_parser=epoch_to_dt,  # this is the parse function
                           header=0)  # first row is header row
        # If the index is int64, that is good enough, no need to convert.
        if isinstance(hist.index[-1], np.int64):
            print('Ingested hist from filePath=%s' % (plan.fullFileName,))
            return hist
        else:  # if index is string, needs to convert index from string to epoch second
            hist = pd.read_csv(plan.fullFileName,
                               index_col=0,  # first column is index column
                               parse_dates=True,  # first column should be parse to pd.Timestamp
                               header=0)  # first row is header row
            print('Ingested hist from filePath=%s' % (plan.fullFileName,))
            hist.rename(columns=lambda x: x.lower(), inplace=True)
            return convert_hist_using_timestamp_to_epoch(hist)
