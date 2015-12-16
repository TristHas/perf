import os

###
###     Directory
###
# Folder Structure
PARENT_DIR      = '/tmp'
DIR_NAME        = 'bench_dialog'
ROOT_DIR        = os.path.join(PARENT_DIR, DIR_NAME)
WORK_DIR        = os.path.join(ROOT_DIR, 'src')
DATA_DIR        = os.path.join(ROOT_DIR, 'data')
LOG_DIR         = os.path.join(ROOT_DIR, 'log')

###
###     System Watch var
###
SYS_MEM_DATA    = ["MemFree","Buffers","Cached","MemAvailable"]
SYS_CPU_DATA    = ["usr_time","nice_time","sys_time","io_time","irq_time","softirq_time","idle_time"]
SYS_CPU_OTHER   = ["time", 'load']
LOAD_AVG        = ["lavg_1","lavg_5","lavg_15"]
PROC_CPU_DATA   = ["time","utime","cutime","stime","cstime","majflt","majcfault"]
PROC_MEM_DATA   = ["VmSize","VmPeak","VmStk","VmRSS", "Threads"]
TIMESTAMPS      = ['timestamp']
HEADERS         = {'system': SYS_CPU_OTHER + LOAD_AVG + SYS_CPU_DATA + SYS_MEM_DATA + TIMESTAMPS,
                   'process': PROC_CPU_DATA + PROC_MEM_DATA + TIMESTAMPS,
                   }

###
###     Net communication
###
SOC_PORT_CTRL   = 6004
SOC_PORT_DATA   = 6006
LOGIN           = 'nao'
PWD             = 'nao'

###
###     Logging
###
V_SILENT        = -1
V_ERROR         = 0
V_WARN          = 1
V_INFO          = 2
V_VERBOSE       = 3
V_DEBUG         = 4

DATA_CLIENT_LOG_FILE    = os.path.join(LOG_DIR, 'recv_data_client.log')
MAIN_CLIENT_LOG_FILE    = os.path.join(LOG_DIR, 'main_client.log')
PROC_CLIENT_LOG_FILE    = os.path.join(LOG_DIR, 'proc_data_client.log')
PRINT_CLIENT_LOG_FILE   = os.path.join(LOG_DIR, 'print_client.log')

DATA_SERVER_LOG_FILE    = os.path.join(LOG_DIR, 'data_server.log')
MAIN_SERVER_LOG_FILE    = os.path.join(LOG_DIR, 'main_server.log')
CPU_SERVER_LOG_FILE     = os.path.join(LOG_DIR, 'cpu_server.log')

###
###     DEFAULT var
###
D_VERB          = V_DEBUG
D_TIMEOUT       = 10000
D_STEP          = 1
CSV_SEP         = ','

###
###     Print var
###
PRINT_TIC       = 60

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
MSG_SEP         = '&&&'
