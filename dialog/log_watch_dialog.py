#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from ..log.log_watch import LogWatch

class LogWatchDialog(LogWatch):
    def __init__(self, ip, root_dir = '/tmp/log_watch_dialog', message_category = 'Dialog'):
        super(LogWatchDialog, self).__init__(ip, root_dir, message_category = message_category)
        LogWatch.category_filter = 'Dialog'

    ###
    ### result processing functions
    ###
    def has_deserialized_topics(self):
        pass

    def has_deserialized_model(self):
        pass

    def get_load_time(self):
        try:
            logs = self.get_log_subset(substring = 'Load topic')
            timestamps = [x[0] for x in logs]
            ret_val = np.max(timestamps) - np.min(timestamps)
        except Exception:
            return None
        return ret_val

    def get_bundle_compile_time(self, bundle):
        try:
            begin = 'Compile bundle: {}'.format(bundle)
            log = self.get_log_subset(substring = 'Bundle compilation time', begin = begin, end = 'Bundle compilation time')
            ret_val = float(log[0][1].split()[-2]) / 1000
        except Exception:
            return None
        return ret_val

    def get_model_compile_time(self, bundle):
        try:
            begin = 'Compile bundle: {}'.format(bundle)
            log = self.get_log_subset(substring = '...model compiled', begin = 'Compile bundle: {}'.format(bundle), end = '...model compiled')
            ret_val = float(log[0][1].rsplit()[-2].strip('(')) / 1000
        except Exception:
            return None
        return ret_val

    def get_reco_compile_time(self, bundle, language):
        try:
            bundle_log = self.get_log_subset(substring = '', begin = 'Compile bundle: {}'.format(bundle),
                                             end = 'Bundle compilation time')

            log = self.get_log_subset(substring = 'Speech Recognition: Compilation time', begin = language,
                                      end = 'Speech Recognition: Compilation time', logs = bundle_log)
            ret_val = float(log[0][1].rsplit()[-2]) / 1000
        except Exception:
            return None
        return ret_val

    def get_timestamp_range(self, sequence):
        begin       = ''
        end         = ''
        substring   = ''
        if sequence == 'loading':
            substring = 'Load topic'
        if sequence == 'compile_bundle':
            begin   = 'Compile bundle: welcome'
            end     = 'Bundle compilation time'
        if sequence == 'compile_model':
            begin   = 'compile_bundle'
            end     = '...model compiled'
        if sequence == 'compile_reco_Japanese':
            pass
        if sequence == 'compile_reco_English':
            pass
        log = self.get_log_subset(substring = substring, begin = begin, end = end)
        return [x[0] for x in log]

    def get_error(self, begin = '', end = ''):
        logs = self.get_log_subset(begin = '', end = '')
        error = [x[1] if x <= 2 else False for x in logs]
        return error

