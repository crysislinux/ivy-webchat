import inspect


def getExceptionInfo(e):
    trace = inspect.trace()
    return str(e) + ': ' + trace[0][1] + ', line ' + str(trace[0][2]) + trace[0][4][0]
