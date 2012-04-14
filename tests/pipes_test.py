from useless.pipes import *
   
import unittest

@producer    
def one_by_one():
    for item in ['a', 'b']:
        yield item
        
@worker
def echo2(ITEMS):
    for item in ITEMS:
        yield item
        
@worker
def add(ITEMS, s):
    for item in ITEMS:
        yield item + s
        
@worker
def unique(ITEMS):
    set_ = set()
    for item in ITEMS:
        if item not in set_:
            set_.add(item)
            yield item

@consumer    
def as_list(ITEMS):
    return [i for i in ITEMS]

class ProducerTest(unittest.TestCase):
    def testYouCanTurnAProducerIntoAList(self):
        items = ['a', 'b']
        p = one_by_one()
        self.assertEqual(items, p.as_list())
        
    def testPrintingReturnsAList(self):
        items = ['a', 'b']
        p = one_by_one()
        self.assertEqual(str(items), str(p))
        
    def testYouCanIterateOverTheElements(self):
        items = ['a', 'b']
        p = one_by_one()
        got = [i for i in p]
        self.assertEqual(items, got)
        
    def testPassedInArgumentsOnConstructionAreStored(self):
        @producer
        def echo(list_):
            for item in list_:
                yield item
                
        items = ['b', 'c']
        p = echo(items)
        self.assertEqual(items, p.as_list())
        
    def testConcurrentVersionsOfAProducerDontDisturbEachOther(self):
        @producer
        def echo(list_):
            for item in list_:
                yield item
                
        A = ['A']
        B = ['B']
        p1 = echo(A)
        p2 = echo(B)
        self.assertEqual(p1.as_list(), A)
        self.assertEqual(p2.as_list(), B)
       
class WorkerTest(unittest.TestCase):
    def testTheDescriptorRemovesTheFirstArgument(self):
        w = echo2()
        
    def testCallingAWorkerInjectsTheItems(self):
        items = ['a', 'b']
        w = echo2()
        got = [i for i in w(items)]
        self.assertEqual(items, got)
        
    def testYouCanPipeInItems(self):
        items = ['a', 'b']
        w = echo2()
        pipe = items | w
        
        got = [i for i in pipe]
        self.assertEqual(items, got)

    def testPassedArgumentsOnConstructionAreAvailable(self):
        items = ['a', 'b']
        w = add('C')
        pipe = items | w
        
        got = [i for i in pipe]
        expected = ['aC', 'bC']
        self.assertEqual(got, expected)
        
    def testYouCanPipeTwoWorkersAndSoOn(self):
        items = ['a', 'b']
        w1 = add('C')
        w2 = add('D')
        pipe = items | w1 | w2
        
        got = [i for i in pipe]
        expected = ['aCD', 'bCD']
        self.assertEqual(got, expected)
        
    def testAWorkerCanHaveLocalVars(self):
        items = ['a', 'b', 'a']
        w = unique()
        pipe = items | add('C') | w
        
        got = [i for i in pipe]
        expected = ['aC', 'bC']
        self.assertEqual(got, expected)

    def testEqualityWithOtherWorkers(self):
        from useless.pipes.common import echo
        
        self.assertEqual(echo, echo)

        w1 = [1,2] | echo
        w2 = [1,2] | echo

        self.assertEqual(w1,w2)


        w3 = [1,3] | echo

        self.assertNotEqual(w1,w3)

        @worker
        def echo(items):
            for item in items:
                yield item

        self.assertNotEqual([1,2]|echo(),[1,2]|echo())
        
        
    def testEqualityWithAList(self):
        from useless.pipes.common import echo
        
        w1 = [1,2] | echo
        w2 = [1,2] | echo
        self.assertEqual(w1, [1,2])

    def testAskWhatsInTheChain(self):
        from useless.pipes.common import echo, unique
        items = [1, 2]
        w1 = unique
        w2 = echo
        chain = items | w1 | w2
        
        self.assertEqual(chain.the_chain_to_the_left(), [w2, w1, items])
        
    def testReusableWorkers(self):
        from useless.pipes.common import unique, zip_with

        @worker
        def selectFirst(tuples):
            for first, _ in tuples:
                yield first
                
        self.assertEqual(
           [1,1] | unique |                # [1]
           zip_with([2,2]) | unique |      # [(1,2)]
           selectFirst() | unique | list,  # [1]
           [1]
        )
        
    def testCycleThenRepeat(self):

        def cycle_then_repeat(iter):
            for item in iter:
                yield item

            while True:
                yield item

        iter = cycle_then_repeat([1,2])
        got = []
        for i in range(4):
            got.append(iter.next())

        self.assertEqual([1,2,2,2], got)    

    def testWorkersCanBeCached(self):
        from useless.pipes.common import echo

        @worker
        def spying(items, list_):
            for item in items:
                list_.append(item)
                yield item
                
        @worker
        def echoes(items):
           for item in items:
               yield item

        cache = echoes()
        cache.cache

        spied = []
        spy = spying(spied)
        [1,2] | spy | cache | list
        [1,2] | spy | cache | list

        self.assertEqual(spied, [1,2])

        cache = echoes()
        cache.cache
        
        spied = []
        spy = spying(spied)
        [3,4] | spy | cache | (echo, echo) | list

        self.assertEqual(spied, [3,4])

    def testYouCanCloneAWorker(self):
        from useless.pipes.common import echo

        clone = echo.clone()
        clone.cache

        self.assertFalse(echo._cache)

    def testTransformingWorkers(self):
        from useless.pipes.common import echo

        @worker
        def add_one(items):
            for item in items:
                yield item + 1

        @worker
        def dummy(items):
            return items | add_one() | add_one()

        self.assertEqual([4,5], [2,3] | dummy() | list)

        @worker
        def cat(items):
            return items | dummy() | add_one()

        self.assertEqual([5,6], [2,3] | cat() | list)

    def testConcatWorkers(self):
        from useless.pipes.common import concat, echo
        
        @worker
        def add_one(items):
            for item in items:
                yield item + 1

        it = add_one() | echo | add_one()

        self.assertEqual([4,5], [2,3] | concat(it) | list)
        self.assertEqual([6,7], [2,3] | concat(it) | concat(it) | list)
        
class WorkingWithListOfTuples(unittest.TestCase):
    def testTheTupleizeWorker(self):
        from useless.pipes.common import echo
        from useless.pipes.tupleize import tupleize
        
        w = [1,2] | tupleize(echo)

        self.assertEqual([(1,),(2,)], w | list)

    def testAutomaticallyAddLastGeneratorToEachLeftEnd(self):
        from useless.pipes.common import from_list,echo,unique
                
        self.assertEqual(from_list([1,3]) | (echo, ) | list, [(1,),(3,)])        
        self.assertEqual(from_list([1,2]) | (echo, echo) | list, [(1,1),(2,2)])
        
#        assert False
        
    def testWhenThereIsNoUnboundLeftEndJustExecuteThePipe(self):
        from useless.pipes.common import echo,unique
        self.assertEqual(
           [1,2,4] | echo | 
           ([1,1] | unique, [3,3] | unique) # in the tuple we 'start' 
                                            # with a new pipe 
           | list, 
           [(1,3)]
        )
        
    def testALiteralValueJustRepeats(self):
        from useless.pipes.common import from_list,echo
        
        self.assertEqual(
           from_list([1,2]) | ('foo', echo) | list, 
           [('foo',1),('foo',2)]
        )

    def testTupleOnTheLeftMostSideWorkLikeProducers(self):
        from useless.pipes.common import from_list, echo, unique
        
        # using 'literal' iterables
        self.assertEqual(
           ([1,2],[3,4]) | echo | list,
           [(1,3),(2,4)]
        )
        #using useless.pipess: a worker and a producer
        self.assertEqual(
           ([1,2] |  unique, from_list([3,4])) | echo | list,
           [(1,3),(2,4)]
        )
        #'literal' values repeat
        self.assertEqual(
           ('foo', [1,2]) | echo | list,
           [('foo',1),('foo',2)]
        )
        
        
class ConsumerTest(unittest.TestCase):            
    def testReturnsInsteadOfYields(self):
        items = ['a', 'b']
        c = as_list()
        
        self.assertEqual(c(items), items)
        
    def testConsumersArePipeable(self):
        items = ['a', 'b']
        c = as_list()
        pipe = items | c
        
        self.assertEqual(pipe, items)
        
    def testShorthandConsumers(self):
        items = ['a', 'b', 'a']
        pipe = items | unique() | list
        self.assertEqual(pipe, ['a','b'])
        
    def testSorted(self):
        items = ['a', 'b', 'a']
        @consumer
        def s(ITEMS, **kw):
            return sorted(ITEMS, **kw)
        s = lambda items, **kw: sorted(items, **kw)
        s = consumer(lambda items, **kw: sorted(items, **kw))
        pipe = items | unique() | s(reverse=True) 
        
        self.assertEqual(pipe, ['b', 'a'])
        
    def testSideeffect(self):
        l = []
        @worker
        def effect(ITEMS, list_):
            for i in ITEMS:
                list_.append(i)
                yield i
                
        items = [1,2,3]
        pipe = items | effect(l) | unique() 
        pipe |= as_list()
        
        self.assertEqual(l, items)
        
    def testChainability(self):
        u2 = consumer(lambda items:items|unique())
        
        self.assertEqual([1,2,2,3] | u2() | as_list(), [1,2,3])
        
if __name__ == '__main__':
    unittest.main()

