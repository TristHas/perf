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
    def __init__(self, adict, headers, targets, data):
        if not os.path.isdir(NAO_DATA_DIR):
            os.makedirs(NAO_DATA_DIR)

        self.log = Logger(CPU_LOG_FILE, adict['v'])
        self.step = adict['step']
        self.timeout = int(adict['timeout'] / self.step)

        # Sync variables
        self.transmit = data
        self.run = True
        self.keep_running = False
        self.is_transmitting = False

        # Record var
        self.sys_prev_cpu = {key:0 for key in SYS_CPU_DATA}
        self.time = 0
        self.load = 0
        self.proc = dict()
        non_valid_processes = []
        for process in targets['process']:
            pid = self._get_pid(process)
            if pid:
                self.proc[process] = {
                        'pid':pid,
                        'prev_cpu':{key:0 for key in PROC_CPU_DATA},
                    }
            else:
                non_valid_processes.append(process)
                self.log.warn("Non valid process {}. Skipping this process".format(process))
        targets['process'] = [proc for proc in targets['process'] if (proc not in non_valid_processes)]
        self.log.info("Targets for record are {}".format(targets['process']))

        self.thr_start = threading.Thread(target = self._launch_record, name = 'cpu_thread', args=(), kwargs=adict)
        self.log.info('starting CPU Thread')
        self.thr_start.start()
        self.log.debug('CPU Thread started')

    def quit(self):
        self.stop()
        self.run = False

    def start(self):
        """
        Starts recording process async.
        """
        ## self.directory = os.path.join(NAO_DATA_DIR, time.ctime())
        ## os.makedirs(self.directory)
        self.keep_running=True
        print 'start start'

    def stop(self):
        """
        Stops the recording process
        """
        self.keep_running = False
        time.sleep(self.step)

    # init helpers
    def _get_pid(self, process):
        ps_result = os.popen('ps aux | grep {}'.format(process)).readlines()
        tmp = []
        for res in ps_result:
            if 'record_server' in res:
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
    def _init_record(self):
            self.is_transmitting = True

    def _end_record(self):
            self.transmit.put('end')
            self.is_transmitting = False

    def _record(self, tmp):
            self.transmit.put(tmp)

    def _launch_record(self, **adict):
        count = 0                                                   # record loop var init
        step = self.step
        timeout = self.timeout
        self._init_record()
        while self.run:                # Timeout + stop() message
            if self.keep_running and count < timeout:
                tmp = {}
                tme = self._get_time()                                  # sys time is used for several measures
                keys = self.proc.keys()
                keys.append('system')
                for key in keys:
                    if key == 'system':
                        tmp[key] = self.get_sys_data(tme)
                    else:
                        tmp[key] = self.get_proc_data(tme, key)
                self._record(tmp)
                count += step
                time.sleep(step)
            else:
                time.sleep(1)
        self._end_record()
        print 'end of thread record'

    # record helpers

    def get_sys_data(self, tme):
        tmp_sys = self.get_sys_cpu_stat(tme)                        # SYS_MEM_DATA
        tmp_sys.update(self.get_sys_mem_stat())                     # SYS_CPU_DATA
        tmp_sys.update(self.get_load_avg())                         # LOAD_AVG
        tmp_sys['time'] = tme                                       # SYS_CPU_OTHER
        tmp_sys['load'] = 100 * (1 - tmp_sys['idle_time'])          # add frag, pgfault, any other?
        return tmp_sys

    def get_proc_data(self,tme, key):
        tmp_proc = self.get_proc_cpu_stat(key, tme)                 # PROC_CPU_DATA
        tmp_proc.update(self.get_proc_mem_stat(key))                # PROC_MEM_DATA
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
            "time": sum(tmp[2:])
        }
        try:
            for key in PROC_CPU_DATA:
                if key == 'time':
                    res[key] = tmp_proc_cpu[key] - self.proc[process]['prev_cpu'][key] / sys_time
                else:
                    res[key] = tmp_proc_cpu[key] - self.proc[process]['prev_cpu'][key] # divide by proc time
                self.proc[process]['prev_cpu'][key] = tmp_proc_cpu[key]
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


