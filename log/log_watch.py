import os
import numpy as np
from qi import Session, logging

### Replace record directory to match bench_dialog's
RECORD_DIRECTORY = "/tmp/bench_dialog/LogWatch"
HEADERS = ('timestamp', 'log')
CSV_SEP = ','

class LogWatch(object):
    is_logging      = False
    dialog_log_records     = []

    def __init__(self, ip, message_start = '', message_stop = 'Not existing One'):
        self.s = Session()
        self.s.connect(ip)
        self.log_manager = self.s.service("LogManager")
        self.listener = self.log_manager.getListener()
        # Dialogs var
        self.dialog_signal_id = None
        LogWatch.dialog_message_start = message_start
        LogWatch.dialog_message_stop = message_stop

    def start_watch_dialog(self):
        self.listener.clearFilters()
        self.listener.setLevel(logging.DEBUG)
        self.dialog_signal_id = self.listener.onLogMessage.connect(dialog_preload_timestamp_message)

    def stop_watch_dialog(self):
        if self.dialog_signal_id:
            self.listener.onLogMessage.disconnect(self.dialog_signal_id)

    ###
    ### Helpers
    ###
    def get_log_subset(self, substring = '', begin = '', end = '', logs = False):
        if not logs:
            logs = LogWatch.dialog_log_records
        subset = []
        appending = False
        for log in logs:
            if begin in log[1]:
                appending = True
            if substring in log[1] and appending:
                subset.append(log)
            if end in log[1]:
                appending = False
        return subset

    def dump_logs(self, file_name):
        if not os.path.isdir(RECORD_DIRECTORY):
            os.makedirs(RECORD_DIRECTORY)
        file_path = os.path.join(RECORD_DIRECTORY, file_name)
        with open(file_path, 'w') as f:
            f.write(CSV_SEP.join([x for x in HEADERS]))
            for line in LogWatch.dialog_log_records:
                f.write(CSV_SEP.join([str(x) for x in line]))

    ###
    ### Access functions
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

###
###     Callbacks
###
# Dialog
def dialog_preload_timestamp_message(mess):
    if 'Dialog' in mess['category']:
        if LogWatch.dialog_message_start in mess['message']:
            LogWatch.is_logging = True
        if LogWatch.is_logging:
            LogWatch.dialog_log_records.append((mess['timestamp']['tv_sec'], mess['message'], mess['level']))
        if LogWatch.dialog_message_stop in mess['message']:
            LogWatch.is_logging = False

def general_log_messages(mess):
    if LogWatch.dialog_message_start in mess['message']:
        LogWatch.is_logging = True
    if LogWatch.is_logging:
        LogWatch.dialog_log_records.append((mess['timestamp']['tv_sec'], mess['message'], mess['level']))
    if LogWatch.dialog_message_stop in mess['message']:
        LogWatch.is_logging = False

if __name__ == '__main__':
    ip = '10.0.132.205'
    x = LogWatch(ip = ip)
    x.start_watch_dialog()
    s = Session()
    s.connect(ip)
    dialog = s.service('ALDialog')
    dialog.deleteSerializationFiles()
    dialog._resetPreload()
    print 'Preloading ...'
    dialog._preloadMain()
    x.stop_watch_dialog()
    print LogWatch.dialog_log_records

    print x.get_bundle_compile_time('welcome'),
    print x.get_model_compile_time('welcome'),
    print x.get_reco_compile_time('welcome', 'Japanese'),
    print x.get_reco_compile_time('welcome', 'English'),



