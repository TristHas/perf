#!/usr/bin/env python
# -*- coding: utf-8 -*-

class LogWatchDialog(LogWatch):
    def __init__(self, ip, root_dir = '/tmp/log_watch_dialog', message_category = 'Dialog'):
        super(LogWatchDialog, self).__init__(ip, root_dir, message_category = message_category)
        LogWatch.category_filter = 'Dialog'
