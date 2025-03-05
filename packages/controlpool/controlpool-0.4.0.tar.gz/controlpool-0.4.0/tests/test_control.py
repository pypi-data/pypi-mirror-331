#!/usr/bin/env python3
import sys
sys.path = ["../src"] + sys.path
import controlpool as cp
import time
import os
import secrets

def clear_sqrt(x):
    return x**2

def long_sqrt(x):
    if not secrets.randbelow(5000):
        raise ValueError("Just for fun")
    return clear_sqrt(x)

def controller(controller_terminal):
    sys.stdin = os.fdopen(0)
    while True:
        comm = input()
        spl = comm.split()
        if len(spl) == 0:
            pass
        elif len(spl) == 1 and spl[0] == "info":
            info = controller_terminal.get_info()
            print(info)
        elif len(spl) == 1 and spl[0] == "add":
            status, expl = controller_terminal.add_worker()
            print("Error: " + expl if status else "Ok")
        else:
            try:                
                state = cp.WorkerState[spl[0]]
                if len(spl) != 2 and len(spl) != 3:
                    print("Wrong syntax1")
                    continue
                if len(spl) == 3 and spl[2] != "now":
                    print("Wrong syntax2")
                    continue
                now = len(spl) == 3
                wid = int(spl[1])
                status, expl = controller_terminal.change_worker_state(wid,
                                                                       state,
                                                                       now)
                print("Error: " + expl if status else "Ok")
            except KeyError:
                print("Unknown command")
            except ValueError:
                print("Wrong syntax3")

with cp.Pool(long_sqrt, 20, raise_if_fail=False, controller=controller) as pool:
    res1 = pool.map(range(3000000))
    res2 = list(map(clear_sqrt, range(3000000)))
    print(res2 == res1)
