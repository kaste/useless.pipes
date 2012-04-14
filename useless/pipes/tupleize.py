from itertools import izip, repeat
from useless.pipes import worker, producer

def _expand_tuple(left, tuple_):
    from pipes import Worker
    from common import concat

    def find_left_end(iter):
        while hasattr(iter, 'left'):
            iter = iter.left
        return iter

    iters = []
    for it in tuple_:
        leftmost = find_left_end(it)
        
        if isinstance(leftmost, Worker):
            # When we have a worker on the left side, then it is an unbound one
            # so we automatically bind to the 'left' 
            iters.append(left | concat(it))
        elif not hasattr(it, '__iter__'):
            # If it's not iterable it is a literal value, we repeat
            iters.append(repeat(it))
        else:
            # We have an iterator we can 'execute'
            iters.append(it)
    return iters

@worker
def tupleize(items, *tuple_):
    iters = _expand_tuple(items, tuple_)
    return izip(*iters)

@producer
def tuple_generator(*tuple_):
    iters = _expand_tuple(None, tuple_)
    return izip(*iters)

