#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qi import Session
import os, threading, time

TIME_STEP = 1
HEADERS = ['time_stamp', 'life_state', 'focused_activity', 'running_behaviors', '\n']
DATA_PATH = '/tmp/bench'
CSV_SEP = ','
BEHAVIOR_SEP = '$$$'

class NaoqiWatcher(object):
    def __init__(self, ip):
        self.s = Session()
        self.s.connect(ip)
        self.a_life = self.s.service('ALAutonomousLife')
        self.behavior_manager = self.s.service('ALBehaviorManager')
        self.is_recording_activity = False
        self.file = None

    def start_activity_record(self, dirname = 'naoqi_watcher'):
        if not self.is_recording_activity:
            self.is_recording_activity = True
            directory = os.path.join(DATA_PATH, dirname)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, 'activity')
            self.file = open(file_path, 'w')
            self.file.write(CSV_SEP.join(HEADERS))
            thr = threading.Thread(target = self.process_loop, args = ())
            thr.start()
            return file_path

    def stop_activity_record(self):
        self.is_recording_activity = False

    def process_loop(self):
        while self.is_recording_activity:
            time_stamp = str(time.time())
            life_state = self.a_life.getState()
            focused_activity = self.a_life.focusedActivity()
            runniung_behaviors = BEHAVIOR_SEP.join(self.behavior_manager.getRunningBehaviors())
            to_write = [time_stamp, life_state, focused_activity, runniung_behaviors, '\n']
            self.file.write(CSV_SEP.join(to_write))
            time.sleep(TIME_STEP)
        self.file.close()
        self.file = None

def main(ip):
    nao = NaoqiWatcher(ip)
    nao.start_activity_record()
    raw_input()
    nao.stop_activity_record()

if __name__ == '__main__':
    ip = '10.0.132.205'
    main(ip)
