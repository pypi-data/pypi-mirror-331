# 1730, Sat Feb  1 2025 (NZDT)
#
# dbg_print.py:  debug printing function
#
# Copyright 2025, Nevil Brownlee, Taupo NZ

debug = False  # global variable

def dbg_print(txt):
    if debug:
        print(txt)
