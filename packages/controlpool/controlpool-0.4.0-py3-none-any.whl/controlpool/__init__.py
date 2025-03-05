#!/usr/bin/env python3
import enum
import itertools
import traceback
import multiprocessing as mp
import multiprocessing.connection as connection
from ._messages import *


class Pool:
    '''
    Class of processes pool for controllable calculation.
    '''

    def __init__(self, func, processes, *, worker_params=None,
                 marks=itertools.repeat(None), raise_if_fail=True,
                 controller=None):
        '''
        Constructor.
        func - function to calculate
        worker_params - worker params that pass to func (default - no pass)
        processes - number of worker processes
        marks - (optional) marks of every worker
        riase_if_fail - raise RuntimeError if all workers riase
                        exception or fall
        controller - function that controls pool work
        '''

        outq = mp.SimpleQueue()
        self._worker_params_present = worker_params is not None
        if worker_params is None:
            worker_params = itertools.repeat(None)

        self._workers = [Worker(func, mark, worker_param,
                                self._worker_params_present,
                                mp.Pipe(duplex=False), outq, n)
                         for mark, worker_param, n in
                         zip(marks, worker_params, range(processes))]
        self._func = func
        self._raise_if_fail = raise_if_fail
        self._bus_queue = outq

        if controller is None:
            self._controller = None
        else:
            self._controller = Controller(controller, self._bus_queue)

        self._ready = True  # ready for work (False after close())
        self._reset()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def map(self, *args, **kwargs):
        '''
        Calculate function for every arg in args.

        '''
        return list(self.map_iterable(*args, **kwargs))

    def map_iterable(self, args, return_arg=False):
        '''
        Like map, but return generator instead of list.

        return_arg - return tuple (argument, result), else only result
        
        Newer try to call map_iterable before previous map_iterable
        generator expire!
        '''
        
        if not self._ready:
            raise RuntimeError("Try to map closed pool")

        if self._results is not None:
            raise RuntimeError("Try to map, but previous map is not complete")

        self._init_map(args)
        while True:
            inmessage = self._bus_queue.get()
            if isinstance(inmessage, WorkerMessage):
                self._worker_message_processing(inmessage)
            elif isinstance(inmessage, ControllerMessage):
                self._controller_message_processing(inmessage)
            else:
                raise RuntimeError("Unknown inmessage class")

            while self._res_i in self._results:
                res = self._results.pop(self._res_i)
                yield res if return_arg else res[1]
                self._res_i += 1

            # check that we done all jobs
            if not self._args_present and self._check_workers_ready():
                self._reset()
                return

    def close(self):
        '''
        Destroy all workers.
        '''
        # repeat close do nothing
        if not self._ready:
            return

        self.ready = False
        for woker in self._workers:
            woker.terminate()
        self._workers = []

        if self._controller is not None:
            self._controller.kill()

    def _init_map(self, args):
        '''
        Initialisation of map
        '''

        self._argsi = iter(args)
        self._results = dict()
        self._args_present = True
        self._i = 0
        self._res_i = 0
        for worker in self._workers:
            if worker.state == WorkerState.PAUSED:
                self._give_task(worker)
            if not self._args_present:
                break

    def _worker_message_processing(self, inmessage):
        '''
        Processing inmessage from worker.
        '''
        worker = self._workers[inmessage.sender_number]
        if worker.state != WorkerState.RUN:
            return  # Ignore: status changed by controller

        if isinstance(inmessage, NotDoneMessage):
            if isinstance(inmessage, ExceptionMessage):
                worker.state = WorkerState.EXCEPTION
                worker.exception = inmessage.exception
                if worker.pending_state == WorkerState.KILLED:
                    worker.kill() 
            elif isinstance(inmessage, FallMessage):
                self._add_delayed_task(worker.task)
                worker.kill()
            else:
                raise RuntimeError("Unknown NotDoneMessage class")

            self._add_delayed_task(worker.task)
            self._give_task()  # try to give task to free worker
            if self._raise_if_fail and not self._check_workers_alive():
                exc = '\n'.join([''.join(traceback.format_exception(worker.exception))
                                 for worker in self._workers])
                raise RuntimeError("All worker raise exception\n" + exc)
            return

        if isinstance(inmessage, DoneMessage):
            self._add_result(worker.task, inmessage.result)

        if worker.pending_state == WorkerState.KILLED:
            worker.kill()
            return
        elif worker.pending_state is not None:
            worker.state = worker.pending_state
            worker.pending_state = None

        if worker.state != WorkerState.RUN:
            return
        
        if self._args_present:
            self._give_task(worker)

        if not self._args_present:
            worker.state = WorkerState.PAUSED

    def _controller_message_processing(self, inmessage):
        '''
        Processing inmessage from worker.
        '''

        if isinstance(inmessage, GetInfoMessage):
            info = self._get_info()
            self._controller.send(InfoMessage(info))
        elif isinstance(inmessage, AddWorkerMessage):
            try:
                self._add_worker(inmessage.mark, inmessage.worker_param)
            except OSError as err:
                self._controller.send(RespondMessage(True, str(err)))
            else:
                self._controller.send(RespondMessage())
        elif isinstance(inmessage, ChangeWorkerStateMessage):
            res = self._change_worker_status(inmessage.worker_id,
                                             inmessage.state,
                                             inmessage.now)
            self._controller.send(RespondMessage(*res))
        else:
            self._controller.send(RespondMessage(True, "Unknown Message"))

    def _add_result(self, task, result):
        '''
        Add n-th result to self._results
        '''
        self._results[task.n] = (task.arg, result)

    def _add_worker(self, mark, worker_param):
        n = len(self._workers)
        self._workers.append(Worker(self._func, mark, worker_param,
                 self._worker_params_present, mp.Pipe(duplex=False),
                                    self._bus_queue, n))

    def _change_worker_status(self, worker_id, state, now):
        '''
        Change worker status.
        Return (True, error_message) if error occured, (False, "") otherwise. 
        '''
        if worker_id >= len(self._workers):
            return True, "Unknown worker ID"
        worker = self._workers[worker_id]
        if worker.state.value < 0:
            return True, "Worker killed"
        if (not isinstance(state, WorkerState)) \
           or state == WorkerState.PAUSED \
           or state == WorkerState.EXCEPTION:
            return True, "Invalid worker new state"
        worker.pending_state = None
        if state == worker.state:
            return False, ""  # already in new state, it's ok

        if not now and worker.state == WorkerState.RUN:
            worker.pending_state = state
            return False, ""

        if worker.state == WorkerState.RUN:
            self._add_delayed_task(worker.task)
            self._give_task()

        if state == WorkerState.KILLED:
            worker.kill()
        elif state == WorkerState.RUN:
            worker.state = WorkerState.PAUSED  # if no task available - pause
            self._give_task(worker)
        else:
            worker.state = state

        return False, ""
                          
        
        
    def _give_task(self, worker=None):
        '''
        Give next task to worker.
        If worker is None - give taask for first free worker.
        If no free worker - do nothing.
        If tasks ends self._args_present = False.
        '''

        if worker is None:
            worker = self._find_free_worker()
            if worker is None:  # no free worker
                return  # do nothing

        if len(self._delayed_tasks) == 0:
            try:
                task = Task(next(self._argsi), self._i)
            except StopIteration:
                self._args_present = False
            else:
                worker.give_task(task)
                self._i += 1
        else:
            worker.give_task(self._delayed_tasks.pop())

    def _add_delayed_task(self, task):
        self._delayed_tasks.append(task)
        self._args_present = True

    def _find_free_worker(self):
        '''
        Find first PAUSED worker. None if no PAUSED worker.
        '''
        for worker in self._workers:
            if worker.state == WorkerState.PAUSED:
                return worker

    def _check_workers_ready(self):
        '''
        Check that no workers in RUN state
        '''
        return all([worker.state != WorkerState.RUN
                    for worker in self._workers])

    def _check_workers_alive(self):
        '''
        Check that there is workers in RUN or PAUSE state
        '''
        for worker in self._workers:
            if (worker.state == WorkerState.RUN
                    or worker.state == WorkerState.PAUSED):
                return True
        return False

    def _get_info(self):
        return Info([worker.get_info() for worker in self._workers],
                    len(self._results), len(self._delayed_tasks))

    def _reset(self):
        '''
        Reset state before next map call
        '''
        self._results = None  # temporary results
        self._args_present = None  # args not empty
        self._i = None  # index of next task
        self._res_i = None  # index of next result
        self._argsi = None  # iterator for args
        self._delayed_tasks = []  # tasks delayed due to exceptions and fails


class Info:
    '''
    Information about pool
    '''
    def __init__(self, workers_info: list,
                 complete_tasks: int, delayed_tasks: int):
        self.workers_info = workers_info
        self.complete_tasks = complete_tasks
        self.delayed_tasks = delayed_tasks

    def __str__(self):
        res = "Comlete tasks: %i\nDelayed tasks:%i\n" \
               % (self.complete_tasks, self.delayed_tasks) \
               + "Workers:\nID Mark State Task Exception Param(if present)\n"
        for i, worker_info in enumerate(self.workers_info):
            res += str(i) + " " + str(worker_info) + '\n'
        return res

    def __repr__(self):
        res = "Comlete tasks: %i\nDelayed tasks:%i\n" \
               % (self.complete_tasks, self.delayed_tasks) \
               + "Workers:\nID Mark State Task Exception Param(if present)\n"
        for i, worker_info in enumerate(self.workers_info):
            res += str(i) + " " + repr(worker_info) + '\n'
        return res


class WorkerInfo:
    '''
    Information about worker
    '''
    def __init__(self, mark, state, task, exception, worker_param_present=False,
                 worker_param=None):
        self.mark = mark
        self.state = state
        self.task = task
        self.exception = exception
        if worker_param_present:
            self.worker_param = worker_param

    def __str__(self):
        params = [self.mark, self.state, self.exception]
        if hasattr(self, "worker_param"):
            params.append(self.worker_param)
        return " ".join(map(str, params))

    def __repr__(self):
        params = [self.mark, self.state, self.task, self.exception]
        if hasattr(self, "worker_param"):
            params.append(self.worker_param)
        return " ".join(map(repr, params))


class Task:
    '''
    Class of tasks for worker
    '''

    def __init__(self, arg, n: int):
        '''
        Constructor.
        arg - argument for function
        n - ordinal number of task
        '''

        self.arg = arg
        self.n = n

    def __str__(self):
        return "(" + str(self.n) + ":" + str(self.arg) + ")"

    __repr__ = __str__


class Telephone:
    '''
    Class of objects to communicate with pool
    '''

    def __init__(self, inc: connection.Connection, outq: mp.Queue,
                 number: int):
        '''
        Constructor.
        inq - queue from pool
        outnq - queue to pool
        number - ordinal number of telephone
        '''

        self._inc = inc
        self._outq = outq
        self._number = number

    def send_and_recv(self, message: WorkerMessage) -> PoolMessage:
        '''
        Send the message to pool ang get the reply.
        '''

        message.sender_number = self._number
        self._outq.put(message)
        return self._inc.recv()


class WorkerState(enum.Enum):
    RUN = 0
    PAUSED = 1  # stopped by pool
    STOPPED = 2  # stopped by controller
    EXCEPTION = 10
    KILLED = -1


class Worker:
    '''Worker process class.'''

    def __init__(self, func, mark: object, worker_param,
                 worker_param_present: bool, inc: [connection.Connection]*2,
                 outq: mp.Queue, number: int):
        '''
        Constructor.
        func - the function to execute
        mark - the mark of the workflow
        worker_param - param pass to function
        worker_param_present - is worker_param present?
        inc - list of 2 connection (generate by mp.Pipe) for incomming messages
        outq - Que for outcomming messages
        '''
        self.mark = mark
        if worker_param_present:
            self.worker_param = worker_param
        telephone = Telephone(inc[0], outq, number)
        self.process = mp.Process(target=worker_function,
                                  args=(func, telephone, worker_param,
                                        worker_param_present))
        self.con = inc[1]
        self.task = None  # no starting task, later get from pool
        self.state = WorkerState.RUN
        self.pending_state = None
        self.exception = None  # last exception
        self.process.start()

    def give_task(self, task: Task):
        '''
        Give task to worker
        '''
        if self.state == WorkerState.KILLED:
            raise RuntimeError("Try give_task to KILLED worker")
        self.state = WorkerState.RUN
        self.task = task
        self.con.send(TaskMessage(task.arg))

    def get_info(self):
        if hasattr(self, "worker_param"):
            return WorkerInfo(self.mark, self.state, self.task, self.exception,
                              True, self.worker_param)
        else:
            return WorkerInfo(self.mark, self.state, self.task, self.exception)

    def terminate(self):
        '''
        Terminate worker
        '''
        if self.state == WorkerState.KILLED:
            return

        self.con.send(TerminateMessage())
        self.state = WorkerState.KILLED
        self.process.join(1.0)
        if self.process.is_alive():
            self.process.kill()

    def kill(self):
        '''
        Kill worker without message
        '''
        if self.state == WorkerState.KILLED:
            return

        self.state = WorkerState.KILLED
        if self.process.is_alive():
            self.process.kill()

    def __del__(self):
        self.kill()


class Controller:
    '''Controller process class.'''

    def __init__(self, func, bus_queue):
        '''
        Constructor.
        func - the function to execute
        bus_queue - bus queue of pool
        '''
        self.exclusive_queue = mp.Queue()
        self.out_queue = mp.Queue()
        controller_pult = ControllerTerminal(bus_queue, self.exclusive_queue,
                                             self.out_queue)
        self.process = mp.Process(target=func, args=(controller_pult, ))
        self.process.start()

    def send(self, message):
        '''
        Send message to controller
        '''
        self.out_queue.put(message)

    def get_exclusive(self):
        '''
        Get message from exclusive_queue of controller
        '''
        return self.exclusive_queue.get()

    def kill(self):
        if self.process.is_alive():
            self.process.kill()

    def __del__(self):
        self.kill()


class ControllerTerminal:
    '''Connection between controller process and pool process'''

    def __init__(self, bus_queue, exclusive_queue, in_queue):
        '''
        Constructor.
        bus_queue - bus queue of pool
        exclusive_queue - exclusive queue
                          (like bus_queue, but for controller only)
        in_queue - queue from pool to controller
        '''
        self._bus_queue = bus_queue
        self._exclusive_queue = exclusive_queue
        self._in_queue = in_queue
        self._current_outq = self._bus_queue  # current output queue

    def get_info(self):
        message = self._send_and_get(GetInfoMessage())
        return message.info

    def add_worker(self, mark=None, worker_param=None):
        message = AddWorkerMessage(mark, worker_param)
        r_message = self._send_and_get(message)
        return r_message.error, r_message.explanation

    def change_worker_state(self, worker_id, state, now = False):
        message = ChangeWorkerStateMessage(worker_id, state, now)
        r_message = self._send_and_get(message)
        return r_message.error, r_message.explanation

    def _send_and_get(self, message: ControllerMessage):
        self._current_outq.put(message)
        return self._in_queue.get()


def worker_function(func, telephone: Telephone, worker_param,
                    worker_param_present: bool):
    '''
    Worker processes function.
    func - function for calculation
    telephone - Telephone for communication with pool
    '''

    message = telephone.send_and_recv(ReadyMessage())

    while True:
        if isinstance(message, TerminateMessage):
            break
        try:
            if worker_param_present:
                result = func(worker_param, message.arg)
            else:
                result = func(message.arg)
        except Exception as exception:
            message = telephone.send_and_recv(ExceptionMessage(exception))
        except:
            telephone.send_and_recv(FallMessage())
            raise
        else:
            message = telephone.send_and_recv(DoneMessage(result))
