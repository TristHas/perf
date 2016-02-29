import os
from qi import Session, logging

### FIXME
# Then replace get_log_subset and get_timestamp_range by file access functions
# dump_logs should then be deprecated
### Replace record directory to match bench_dialog's

RECORD_DIRECTORY = "LogWatch"
HEADERS = ('timestamp', 'log', 'level')
CSV_SEP = ','

class LogWatch(object):
    is_logging      = False
    log_records     = []

    def __init__(self, ip, root_dir = '/tmp/log_watcher', message_start = '', message_stop = 'No way this exists in the logs', message_category = ''):
        self.s = Session()
        self.s.connect(ip)
        self.log_manager = self.s.service("LogManager")
        self.listener = self.log_manager.getListener()
        self.root_dir = root_dir
        self.signal_id = None
        self.file_path = None
        LogWatch.message_start = message_start
        LogWatch.message_stop = message_stop
        LogWatch.category_filter = message_category
        self.cb = log_callback


    def start_watch(self, file_name = 'log_watch', level = logging.DEBUG):
        record_dir = os.path.join(self.root_dir, RECORD_DIRECTORY)
        if not os.path.isdir(record_dir):
            os.makedirs(record_dir)
        file_path = os.path.join(record_dir, file_name)
        LogWatch.file = open(file_path, 'w')
        LogWatch.file.write(CSV_SEP.join([x for x in HEADERS]))
        self.listener.clearFilters()
        self.listener.setLevel(level)
        self.signal_id = self.listener.onLogMessage.connect(self.cb)
        self.file_path = file_path

    def stop_watch(self):
        if self.signal_id:
            self.listener.onLogMessage.disconnect(self.signal_id)
            self.signal_id = None
            LogWatch.file.close()
            return True
        else:
            return False

    ###
    ### Helpers
    ###
    def get_log_subset(self, substring = '', begin = '', end = '', logs = False):
        if not logs:
            logs = open(self.file_path)
            #logs = LogWatch.log_records
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

    #def dump_logs(self, file_name):
    #    record_dir = os.path.join(self.root_dir, RECORD_DIRECTORY)
    #    if not os.path.isdir(record_dir):
    #        os.makedirs(record_dir)
    #    file_path = os.path.join(record_dir, file_name)
    #    with open(file_path, 'w') as f:
    #        f.write(CSV_SEP.join([x for x in HEADERS]))
    #        for line in LogWatch.log_records:
    #            f.write(CSV_SEP.join([str(x) for x in line]))

    def get_timestamp_range(self, substring, begin, end):
        log = self.get_log_subset(substring = substring, begin = begin, end = end)
        return [x[0] for x in log]


###
###     Callback
###
# Dialog
def log_callback(mess):
    if LogWatch.category_filter in mess['category']:
        if LogWatch.message_start in mess['message']:
            LogWatch.is_logging = True
        if LogWatch.is_logging:
            LogWatch.file.write(CSV_SEP.join([str(mess['timestamp']['tv_sec']), mess['message'], str(mess['level']), '\n']))
        if LogWatch.message_stop in mess['message']:
            LogWatch.is_logging = False


