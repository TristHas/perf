#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cProfile
from printer import main

if __name__ == '__main__':
    cProfile.run('main()')
