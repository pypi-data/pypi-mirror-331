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
               controller_terminal.add_worker]*0 \
               + [lambda: controller_terminal.change_worker_state(wid,cp.WorkerState.RUN,now)
                  for wid in range(11) 
                  for now in (True, False)]
           
    while True:
        time.sleep(0.001)
        wid = secrets.randbelow(100)
        now = secrets.choice([True, False])
        print(wid, now)
        print(controller_terminal.change_worker_state(wid,cp.WorkerState.RUN,now))
        print(controller_terminal.get_info())

with cp.Pool(long_sqrt, 10, raise_if_fail=False, controller=controller) as pool:
    N = 100000
    res1 = pool.map(range(N))
    res2 = list(map(clear_sqrt, range(N)))
    print(res2 == res1)
