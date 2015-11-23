import os

###
###     Directory
###
# Ubuntu /home/tristan/workspace/perf
LOCAL_WORK_DIR  = '/Users/d-fr-mac0002/Desktop/dialog/projects/perf'      #os.path.dirname(os.path.realpath("__file__"))
LOCAL_DATA_DIR  = os.path.join(LOCAL_WORK_DIR, 'data')
NAO_HOME        = "/home/nao"
NAO_WORK_DIR    = os.path.join(NAO_HOME, 'bench_dialog')
NAO_DATA_DIR    = os.path.join(NAO_HOME, 'bench_data')
CSV_SEP         = ','

###
###     System Watch var
###
SYS_MEM_DATA    = ["MemFree","Buffers","Cached"]#,"MemAvailable"]
SYS_CPU_DATA    = ["usr_time","nice_time","sys_time","io_time","irq_time","softirq_time","idle_time"]
SYS_CPU_OTHER   = ["time", 'load']
LOAD_AVG        = ["lavg_1","lavg_5","lavg_15"]
PROC_CPU_DATA   = ["time","utime","cutime","stime","cstime","majflt","majcfault"]
PROC_MEM_DATA   = ["VmSize","VmPeak","VmStk","VmRSS", "Threads"]

###
###     Net communication
###
# ubuntu "192.168.0.15"
IP_1            = "10.0.206.47"
IP_2            = "10.0.128.144"
SOC_ADR_REMOTE  = IP_1
SOC_ADR_LOC     = IP_2
SOC_PORT_CTRL   = 6004
SOC_PORT_DATA   = 6006
LOGIN           = 'nao'
PWD             = 'nao'

###
###     Logging
###
V_SILENT        = 0
V_WARN          = 1
V_INFO          = 2
V_VERBOSE       = 3
V_DEBUG         = 4
DATA_LOG_FILE   = os.path.join(NAO_DATA_DIR, 'data.log')
SERV_LOG_FILE   = os.path.join(NAO_DATA_DIR, 'server.log')
CPU_LOG_FILE    = os.path.join(NAO_DATA_DIR, 'cpu.log')
CLIENT_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'cpu.log')



###
###     Print var
###
PRINT_TIC       = 60


###
###     Test Purposes
###
PROCESSES       = 'qtcreator naoqi-service'


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



