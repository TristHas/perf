#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cProfile
from printer import main

if __name__ == '__main__':
    cProfile.run('main()')


import cProfile
from qi import Session
s = Session()
s.connect('localhost')
dialog = s.service('ALDialog')
cProfile.run('dialog._preloadMain()')
