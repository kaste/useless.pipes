from itertools import izip, repeat
import copy

__all__ = ['producer','worker','consumer']

def producer(func):
    def wrapper(*a, **kw):
        def f():
            return func(*a, **kw)
        f.__name__ = func.__name__
        return Producer(f)
    
    return wrapper
    
def worker(func):
    def wrapper(*a, **kw):
        def f(iter):
            return func(iter, *a, **kw)
        f.__name__ = func.__name__
        return Worker(f)
    
    return wrapper

def consumer(func):
    def wrapper(*a, **kw):
        def f(iter):
            return func(iter, *a, **kw)
        f.__name__ = func.__name__
        return Consumer(f)
    
    return wrapper

class Pipeable(object):
    def __init__(self, target):
        super(Pipeable, self).__init__()
        self.target = target
   
    def __eq__(self, other):
        if isinstance(other, Worker):
            if self.target != other.target:
                return False
            else:
                return self.left == other.left \
                    if hasattr(self,'left') and hasattr(other,'left') else True
        elif isinstance(other, list):
            return self | list == other
        
    def as_list(self):
        return list(self)
        
    def __str__(self):
        return str(self.as_list())
    
class HasLeftSide():
    def __call__(self, iter=None):
        if not iter and not hasattr(self, 'left'):
            raise Exception, "Unbound, hence not callable."
        iter = iter or self.left
        return self.target(iter)
    
    def the_chain_to_the_left(self):
        chain = [self]
        iter = self
        while hasattr(iter,'left'):
            iter = iter.left
            chain.append(iter)
        return chain
            
    def clone(self):
        return copy.copy(self)

    def bind(self, left):
        if isinstance(left, tuple):
            from tupleize import tuple_generator
            left = tuple_generator(*left)

        self.left = left
        return self
                             
class HasRightSide():
    def __or__(self, right):
        if isinstance(right, tuple):
            from tupleize import tupleize
            right = tupleize(*right)

        if isinstance(right, HasLeftSide):
            return right.__ror__(self)
        else:
            return right(self)
        
class Cacheable(object):
    def __init__(self):
        super(Cacheable, self).__init__()
        self._cache = False
        self.cached = False
    
    @property
    def cache(self):
        self._cache = True
        return self

    def __iter__(self):
        if self._cache:
            if not self.cached:
                self.cached = list(self())
            return iter(self.cached)
        return iter(self())

class Producer(Pipeable, Cacheable, HasRightSide):
    def __call__(self):
        return self.target()
    
class Worker(Pipeable, Cacheable, HasRightSide, HasLeftSide):
    def __ror__(self, left):
        if not self._cache:
            self = self.clone()

        return self.bind(left)
    
    def __repr__(self):
        return 'Worker for %r' % self.target
    
class Consumer(Pipeable, HasLeftSide):
    def __ror__(self, left):
        self.bind(left)
        return self()


