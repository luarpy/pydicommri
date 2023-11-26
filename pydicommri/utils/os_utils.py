#!/bin/env python

import sys

IS_WINDOWS = sys.platform == 'win32' or sys.platform == 'cygwin'
IS_MACOS = sys.platform.startswith('darwin')
IS_LINUX = sys.platform.startswith('linux')

