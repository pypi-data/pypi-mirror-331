#!/usr/bin/env python3
import sys
sys.path = ["../src"] + sys.path
import controlpool as cp
import time
import secrets

def clear_sqrt(x):
    return x**2
def long_sqrt(x):
    if not secrets.randbelow(1000):
        raise ValueError("Just for fun")
    return clear_sqrt(x)



def controller(controller_terminal):
    options = [controller_terminal.get_info,
               controller_terminal.add_worker]*2000 \
               + [lambda: controller_terminal.change_worker_state(wid,state,now)
                  for wid in range(100) for state in cp.WorkerState
                  for now in (True, False)]
               
    while True:
        time.sleep(0.1)
        secrets.choice(options)()

        print(controller_terminal.get_info())

with cp.Pool(long_sqrt, 10, raise_if_fail=False, controller=controller) as pool:
    N = 100000
    res1 = pool.map(range(N))
    res2 = list(map(clear_sqrt, range(N)))
    print(res2 == res1)
