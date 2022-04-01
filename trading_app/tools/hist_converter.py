# coding=utf-8
from BasicPyLib.BasicTools import timestamp_to_epoch, epoch_to_dt, dt_to_epoch, date_to_epoch
import numpy as np
import pandas as pd
import datetime as dt
from sys import exit


def convert_hist_using_datetime_to_epoch(hist):
    if isinstance(hist.index[-1], dt.datetime):
        hist['epoch'] = hist.index.map(dt_to_epoch)
    elif isinstance(hist.index[-1], dt.date):
        hist['epoch'] = hist.index.map(date_to_epoch)
    else:
        exit(__name__ + '::convert_hist_using_datetime_to_epoch: EXIT, cannot handle hist.index type=%s' % (type(hist.index[-1]),))
    hist = hist.reset_index()
    hist = hist.set_index('epoch')
    # assert(isinstance(hist.index[-1], np.int64))
    return hist


def convert_hist_using_timestamp_to_epoch(hist):
    hist['epoch'] = hist.index.map(timestamp_to_epoch)
    hist = hist.reset_index()
    hist = hist.set_index('epoch')
    assert(isinstance(hist.index[-1], np.int64))
    return hist


def convert_hist_using_epoch_to_timestamp(hist):
    hist['timestamp'] = hist.index.map(epoch_to_dt)  # When datetime is used as pd.index, its format is pd.Timestamp, not datetime anymore.
    hist = hist.reset_index()
    hist = hist.set_index('timestamp')
    assert(isinstance(hist.index[-1], pd.Timestamp))  # When datetime is used as pd.index, its format is pd.Timestamp, not datetime anymore.
    return hist
