#!/usr/bin/env python3


class WorkerMessage:
    '''
    Base class for message from worker to pool
    '''

    def __init__(self):

        # sender_number is telephone number of sender
        # set when message is sended
        self.sender_number = None


class DoneMessage(WorkerMessage):
    '''
    Class of WorkerMessage. Indicates that task is done.
    '''

    def __init__(self, result):
        '''
        Constructor.
        result - result of function call
        '''

        super().__init__()
        self.result = result


class ReadyMessage(WorkerMessage):
    '''
    Class of WorkerMessage.
    Indicates that worker is ready for first task.
    '''
    pass


class NotDoneMessage(WorkerMessage):
    '''
    Abstract class of WorkerMessage.
    Indicates that worker task fail.
    '''
    pass


class ExceptionMessage(NotDoneMessage):
    '''
    Class of NotDoneMessage. Indicates that the worker is broken.
    '''

    def __init__(self, exception):
        '''
        Constructor.
        exception - exception of last call
        '''

        super().__init__()
        self.exception = exception


class FallMessage(NotDoneMessage):
    '''
    Class of NotDoneMessage. Indicates that the worker is fall and exit.
    '''


class PoolMessage:
    '''
    Base class for message from pool to worker
    '''
    pass


class TaskMessage(PoolMessage):
    '''
    Class of PoolMessage. Give task to worker.
    '''

    def __init__(self, arg):
        '''
        Constructor.
        arg - argument for func
        '''

        super().__init__()
        self.arg = arg


class TerminateMessage(PoolMessage):
    '''
    Class of PoolMessage. Terminate worker.
    '''

    def __init__(self):
        super().__init__()


class ControllerMessage:
    '''
    Base class for message from controller to pool
    '''
    pass


class GetInfoMessage(ControllerMessage):
    '''
    Get info about pool and workers status
    '''
    pass


class AddWorkerMessage(ControllerMessage):
    '''
    Add additional worker
    '''
    def __init__(self, mark=None, worker_param=None):
        '''
        Constructor.
        mark - mark of worker
        worker_param - param that pass to original func.
                       Ignore if not present in map call.
        '''
        self.mark = mark
        self.worker_param = worker_param


class ChangeWorkerStateMessage(ControllerMessage):
    def __init__(self, worker_id, state, now):
        '''
        Constructor.
        worker_id - worker number (ID)
        state - WorkerState (but not PAUSED or EXCEPTION)
        now - change state now (True) or after complete current task (False)
        '''
        self.worker_id = worker_id
        self.state = state
        self.now = now


class PoolControllerMessage:
    '''
    Base class for message from pool to controller
    '''
    pass


class InfoMessage(PoolControllerMessage):
    '''
    Info about pool and workers status
    '''
    def __init__(self, info):
        super().__init__()
        self.info = info


class RespondMessage(PoolControllerMessage):
    '''
    Respond message
    '''
    def __init__(self, error=False, explanation=""):
        '''
        Constructor.
        error - is there is error
        message - error explanation
        '''
        self.error = error
        self.explanation = explanation
