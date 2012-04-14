from pipes import producer, worker, consumer
from itertools import izip, repeat
from collections import defaultdict

@worker
def unique(items):
    set_ = set()
    for item in items:
        if item in set_: continue
        
        set_.add(item)
        yield item
unique = unique()
        
@consumer
def length(items):
    i = 0 
    for _ in items:
        i += 1
    return i
length = length()

@worker
def join_each_by(items, char=''):
    for item in items:
        yield char.join(item)
join_each = join_each_by(char='')

@consumer
def first(items):
    for item in items:
        return item
first = first()

@worker
def group(items):
    d = defaultdict(int)
    for item in items:
        d[item] += 1
        
    for key, value in d.iteritems():
        yield (key, value)
group = group()

@consumer
def sort(items, key=None, reverse=False):
    return sorted(items, key=key, reverse=reverse)

@consumer
def zip_with(*items):   
    return izip(*items)

@worker 
def echo(items):
    for item in items:
        yield item
echo = echo()

@producer
def from_list(items):
    for item in items:
        yield item

@worker
def concat(items, worker):
    # We want something like items | w, but since we don't have an idea
    # of a pipe or chain of workers, w represents always the rightmost
    # worker. 
    # When we do something like items | leftend(w), this breaks the 
    # chain, because on bind we also copy or 'clone' the worker. Hence:
    # we must walk to the left, and rebind every worker up to the right
    #            [ A  -- B  -- w
    #   [ items -- A' -- B' -- w'

    chain = worker.the_chain_to_the_left()

    left = items
    while chain:
        current_worker = chain.pop()
        cloned_worker = left | current_worker
        left = cloned_worker
    return cloned_worker




#####################################################

if __name__ == '__main__':
    assert [('a','b'),('c','d')] | join_each | list == ['ab','cd']
    assert [('a','b'),('c','d')] | join_each_by(';') | list == ['a;b','c;d']
    
    assert ['a','b'] | zip_with(['c','d']) | list == [('a','c'),('b','d')]
    
    assert [1,2] | first == 1
    
    assert [1,2,3] | length == 3
    
    assert [1,2,1] | group | list == [(1,2),(2,1)]
    
    assert [3,2,1] | sort() | [1,2,3]
    
    assert [1,2,1] | unique | list == [1,2]