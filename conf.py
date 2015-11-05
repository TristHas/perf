import os

###
###     Directory
###
LOCAL_WORK_DIR  = '/Users/d-fr-mac0002/Desktop/dialog/perf'#os.path.dirname(os.path.realpath("__file__"))
LOCAL_DATA_DIR  = os.path.join(LOCAL_WORK_DIR, 'data')
NAO_HOME        = "/home/nao"
NAO_WORK_DIR    = "/home/nao/bench_dialog"
NAO_DATA_DIR    = os.path.join(NAO_HOME, 'bench_data')
BENCH_DIR       = '/home/nao/bench_dialog'
CSV_SEP         = ','

###
###     System Watch var
###
SYS_MEM_DATA    = ["MemFree","Buffers","Cached","MemAvailable"]
SYS_CPU_DATA    = ["usr_time","nice_time","sys_time","io_time","irq_time","softirq_time","idle_time"]
SYS_CPU_OTHER   = ["time", 'load']
LOAD_AVG        = ["lavg_1","lavg_5","lavg_15"]
PROC_CPU_DATA   = ["time","utime","cutime","stime","cstime","majflt","majcfault"]
PROC_MEM_DATA   = ["VmSize","VmPeak","VmStk","VmRSS", "Threads"]

###
###     Net communication
###
IP_1            = "10.0.206.47"
IP_2            = "10.0.128.144"
SOC_ADR_REMOTE  = IP_1
SOC_ADR_LOC     = IP_2
REMOTE_IP_DEF   = IP_1
SOC_PORT_CTRL   = 6007
SOC_PORT_DATA   = 6006
MESSAGES        = ["start", "stop"]
LOGIN           = 'nao'
PWD             = 'nao'

###
###     CIP var
###
CIP_ADDR        = 'localhost'
CIP_PORT        = 6000
CIP_AUTH        = 'nao'
CIP_MSG         = 'stop'

###
###     Verbosity
###
V_INFO          = 1
V_DEBUG         = 2

###
###     Test Purposes
###
PROCESSES       = 'qtcreator naoqi-service'

###
###     Logging
###
SERV_LOG_INFO   = os.path.join(NAO_DATA_DIR,'log_info')
SERV_LOG_ERROR   = os.path.join(NAO_DATA_DIR,'log_error')

###
###     Ctrl Messages
###
STOP_ALL        = '0'
START_RECORD    = '1'
STOP_RECORD     = '2'
START_SEND      = '3'
STOP_SEND       = '4'
START_STORE     = '5'
STOP_STORE      = '6'
FAIL            = 'fail'
SYNC            = 'sync'

###
###     Server state
###
STATE_STOPPED   = -1
STATE_IDLE      = 0
STATE_RECORD    = 1
STATE_STORE     = 2
STATE_SEND      = 3
STATE_FULL      = 4



