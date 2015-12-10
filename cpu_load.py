import os, time
import threading
from conf import *
from helpers import Logger

#############
#####           Only Compatible 2.5 as is
#####           To make it compatible 2.4 and before
#####           delete MemAvailable field from meminfo in conf
#############

class CPUWatcher(object):
    # Could easily add irq, frag, pgfault, and vmem from bench/cpuload.
    # Which are worth watching?
    def __init__(self, headers, data):
        if not os.path.isdir(NAO_DATA_DIR):
            os.makedirs(NAO_DATA_DIR)

        self.log        = Logger(CPU_LOG_FILE, D_VERB)
        self.step       = D_STEP
        self.timeout    = int(D_TIMEOUT / self.step)

        # Sync variables
        self.transmit = data
        self.run = True

        # Record var
        self.sys_prev_cpu = {key:0 for key in SYS_CPU_DATA}
        self.time = 0
        self.load = 0
        self.proc = dict()

        self.thr_start = threading.Thread(target = self.record_process, name = 'cpu_thread', args=(), kwargs={})
        self.log.info('[MAIN THREAD] starting CPU Thread')
        self.thr_start.start()
        self.log.debug('[MAIN THREAD] CPU Thread started')

    def quit(self):
        #self.stop()
        self.run = False

    def start(self, target):
        """
        Starts recording process async.
        """
        ## self.directory = os.path.join(NAO_DATA_DIR, time.ctime())
        ## os.makedirs(self.directory)
        if target == 'system':
            self.proc['system'] = None
            self.log.info('[MAIN THREAD] Start watching system')
            return True
        else:
            pid = self._get_pid(target)
            if pid:
                self.proc[target] = {
                        'pid':pid,
                        'prev_cpu':{key:0 for key in PROC_CPU_DATA},
                    }
                return True
            else:
                self.log.error("Non valid process {}. Skipping this process".format(target))
                return False

    def stop(self, target):
        """
        Stops the recording process
        """
        if target in self.proc:
            del self.proc[target]
            self.log.info('[MAIN THREAD] Has stopped {}'.format(target))
            return_val = True
        else:
            self.log.error('[MAIN THREAD] Has been asked to stop {} while not recording'.format(target))
            reurn_val = False
        time.sleep(self.step)
        return return_val

    # init helpers
    def _get_pid(self, process):
        print 'ps aux | grep {}'.format(process)
        ps_result = os.popen('ps aux | grep {}'.format(process)).readlines()
        print ps_result
        tmp = []
        for res in ps_result:
            if '--proc' in res:
                tmp.append(res)
            if 'grep' in res:
                tmp.append(res)
        for proc in tmp:
            ps_result.remove(proc)
        if len(ps_result) != 1:
            pid = 0
        else:
            pid = ps_result[0].split()[1]
        return pid

    # record methods
    # refactor files should be handled by server data thread
    # only use transmission queue here

    def _record(self, tmp):
        self.transmit.put(tmp)
        self.log.debug('[CPU Thread] Has put to queue {}'.format(tmp))

    def record_process(self):
        self.log.debug('[CPU THREAD] In thread')
        count = 0                                                   # record loop var init
        while self.run:                # Timeout + stop() message
            if count < self.timeout:
                self.log.debug('[CPU THREAD] Processing')
                tmp = {}
                tme = self._get_time()                                  # sys time is used for several measures
                keys = self.proc.keys()
                for key in keys:
                    if key == 'system':
                        tmp[key] = self.get_sys_data(tme)               
                    else:
                        tmp[key] = self.get_proc_data(tme, key)
                if tmp:
                    self._record(tmp)
                count += self.step
                time.sleep(self.step)
            else:
                self.log.warn('[CPU THREAD] Timeout happened, should we change code to stop process?')
                time.sleep(1)
        print '[CPU THREAD] End of thread record'

    # record helpers

    def get_sys_data(self, tme):
        tmp_sys = self.get_sys_cpu_stat(tme)                        # SYS_MEM_DATA
        tmp_sys.update(self.get_sys_mem_stat())                     # SYS_CPU_DATA
        tmp_sys.update(self.get_load_avg())                         # LOAD_AVG
        tmp_sys['time'] = tme                                       # SYS_CPU_OTHER
        tmp_sys['load'] = 100 * (1 - tmp_sys['idle_time'])          # add frag, pgfault, any other?
        tmp_sys['timestamp'] = time.time()
        return tmp_sys

    def get_proc_data(self,tme, key):
        tmp_proc = self.get_proc_cpu_stat(key, tme)                 # PROC_CPU_DATA
        tmp_proc.update(self.get_proc_mem_stat(key))                # PROC_MEM_DATA
        tmp_proc['timestamp'] = time.time()
        return tmp_proc

    def _get_time(self):
        with open('/proc/stat') as cpu_stat:
            cpu_line = cpu_stat.readline()
        tmp = cpu_line.split()
        tmp = tmp[1:]
        tmp = map(float, tmp)
        now_time = sum(tmp)
        res = now_time - self.time
        self.time = now_time
        return res

    def get_load_avg(self):
        with open('/proc/loadavg', 'r') as load_file:
            line = load_file.readline()
        res = line.split()
        return {LOAD_AVG[i]:float(res[i]) for i in range(3)}

    def get_sys_cpu_stat(self, tme):
        res = dict()
        with open('/proc/stat') as cpu_stat:
            cpu_line = cpu_stat.readline()
        tmp = cpu_line.split()
        tmp = tmp[1:]
        tmp = map(float, tmp)
        tmp_sys_cpu = {
            'usr_time':tmp[0],
            'nice_time':tmp[1],
            'sys_time':tmp[2],
            'idle_time':tmp[3],
            'io_time':tmp[4],
            'irq_time':tmp[5],
            'softirq_time':tmp[6]
        }
        try:
            for key in SYS_CPU_DATA:
                res[key] = (tmp_sys_cpu[key] - self.sys_prev_cpu[key])  / tme
                self.sys_prev_cpu[key] = tmp_sys_cpu[key]
        except KeyError as e:
            print "key error {}".format(e.message)
        return res

    def get_proc_cpu_stat(self, process, sys_time):
        pid = self.proc[process]['pid']
        res = dict()
        with open("/proc/"+str(pid)+"/stat") as cpuinfo:
            line = cpuinfo.read()
        tmp = line.split()
        tmp = tmp[11:17]
        tmp = map(int, tmp)
        tmp_proc_cpu = {
            "utime":tmp[2],
            "cutime":tmp[4],
            "stime":tmp[3],
            "cstime":tmp[5],
            "majflt":tmp[0],
            "majcfault":tmp[1],
            #"time": sum(tmp[2:])
        }
        try:
            for key in PROC_CPU_DATA:
                if key != 'time':
                    res[key] = tmp_proc_cpu[key] - self.proc[process]['prev_cpu'][key] # divide by proc time?
                    self.proc[process]['prev_cpu'][key] = tmp_proc_cpu[key]
            res['time'] = (res['utime'] + res['stime']) / sys_time

        except KeyError as e:
            print "key error {}".format(e.message)
        return res

    def get_sys_mem_stat(self):
        """
            Returns a dict containing infos from /proc/meminfo
                - MemAvailable
                - MemFree
                - Buffers
                - Cached
        """
        res = dict()
        with open('/proc/meminfo') as meminfo:
            mem_list = meminfo.readlines()
        # Optimize if it takes too long
        for line in mem_list:
            tmp = line.split()
            tmp[0] = tmp[0].replace(':', '')
            if tmp[0] in SYS_MEM_DATA:
                res[tmp[0]] = int(tmp[1])
        if len(res) != len(SYS_MEM_DATA):
            raise Exception("Error: wrong parsing of /proc/meminfo")
        return res

    def get_proc_mem_stat(self, process):
        pid = self.proc[process]['pid']
        # Optimize if it takes too long
        res = dict()
        with open("/proc/"+str(pid)+"/status") as meminfo:
            mem_list = meminfo.readlines()
        for line in mem_list:
            tmp = line.split()
            tmp[0] = tmp[0].replace(':', '')
            if tmp[0] in PROC_MEM_DATA:
                res[tmp[0]] = tmp[1]
        return res


