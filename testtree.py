import unittest
from tree import *
import time
import random

class testTree(unittest.TestCase):
    
    # POINT QUERIES
    def testSingleInterval_point(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')

        self.assertEqual(tree.testPoint(0), set())   # Outside of interval
        self.assertEqual(tree.testPoint(50), {'a'})  # Edge point
        self.assertEqual(tree.testPoint(75), {'a'})  # Inside interval
        self.assertEqual(tree.testPoint(100), {'a'}) # Edge point
        self.assertEqual(tree.testPoint(150), set()) # Outside of interval

    def testOverlappingIntervals_point(self):
        # Make a tree, add one interval, test a bunch of points (some that overlap both, some only one, some none)
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        tree.add(75, 125, 'b')

        self.assertEqual(tree.testPoint(0), set())           # Outside both intervals
        self.assertEqual(tree.testPoint(50), {'a'})          # Edge a
        self.assertEqual(tree.testPoint(70), {'a'})          # Inside only a
        self.assertEqual(tree.testPoint(75), {'a', 'b'})     # Edge b
        self.assertEqual(tree.testPoint(80), {'a', 'b'})     # Inside a and b
        self.assertEqual(tree.testPoint(100), {'a', 'b'})    # Edge a
        self.assertEqual(tree.testPoint(110), {'b'})         # Inside only b
        self.assertEqual(tree.testPoint(125), {'b'})         # Edge b
        self.assertEqual(tree.testPoint(130), set())         # Outside both intervals

    def testOverlappingEdges_point(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        tree.add(100, 150, 'b')
        tree.add(150, 200, 'c')

        self.assertEqual(tree.testPoint(0), set())
        self.assertEqual(tree.testPoint(50), {'a'})
        self.assertEqual(tree.testPoint(75), {'a'})
        self.assertEqual(tree.testPoint(100), {'a', 'b'})
        self.assertEqual(tree.testPoint(125), {'b'})
        self.assertEqual(tree.testPoint(150), {'b', 'c'})
        self.assertEqual(tree.testPoint(175), {'c'})
        self.assertEqual(tree.testPoint(200), {'c'})
        self.assertEqual(tree.testPoint(250), set())

    def testNoOverlap_point(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        tree.add(110, 120, 'b')
        
        self.assertEqual(tree.testPoint(0), set())
        self.assertEqual(tree.testPoint(50), {'a'})
        self.assertEqual(tree.testPoint(75), {'a'})
        self.assertEqual(tree.testPoint(100), {'a'})
        self.assertEqual(tree.testPoint(105), set())
        self.assertEqual(tree.testPoint(110), {'b'})
        self.assertEqual(tree.testPoint(115), {'b'})
        self.assertEqual(tree.testPoint(120), {'b'})
        self.assertEqual(tree.testPoint(130), set())

    # RANGE QUERIES
    def testSingleInterval_range(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        self.assertEqual(tree.testRange(0, 10), set())  
        self.assertEqual(tree.testRange(0, 50), {'a'}) 
        self.assertEqual(tree.testRange(0, 75), {'a'}) 
        self.assertEqual(tree.testRange(100, 150), {'a'})
        self.assertEqual(tree.testRange(110, 150), set())

    def testOverlappingEdges_range(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        tree.add(100, 150, 'b')
        tree.add(150, 200, 'c')

        self.assertEqual(tree.testRange(0, 10), set())
        self.assertEqual(tree.testRange(0, 50), {'a'})
        self.assertEqual(tree.testRange(50, 100), {'a', 'b'})
        self.assertEqual(tree.testRange(100, 120), {'a', 'b'})
        self.assertEqual(tree.testRange(100, 150), {'a', 'b', 'c'})
        self.assertEqual(tree.testRange(150, 200), {'b', 'c'})
        self.assertEqual(tree.testRange(180, 210), {'c'})
        self.assertEqual(tree.testRange(ninf, inf), {'a', 'b', 'c'})

    # OTHER FUNCTIONALITY
    def testBalancing(self):
        tree = IntervalTree()
        tree.add(50, 100, 'a')
        tree.add(100, 150, 'b')
        tree.add(150, 200, 'c')
        self.assertLessEqual(tree._root._height, 2)

    def testBiggerTree(self):
        # Bigger example to test balancing and runtime
        tree = IntervalTree()
        for x in range(100):
            tree.add(x, x+1, str(x))
        self.assertLessEqual(tree._root._height, 8)

        # Testing Time
        start = time.time()
        for x in range(100):
            tree.testPoint(x)
        end = time.time()
        self.assertLessEqual(end - start, 0.005)

        # Testing that it actually works
        for x in range(100):
            self.assertEqual(tree.testPoint(x + 0.5), {str(x)}, "Failed on " + str(x))

    def testRandomOrder(self):
        # Make sure that a rotation error isn't raised
        lst = list(range(100))
        random.shuffle(lst)
        tree = IntervalTree()
        for x in lst:
            tree.add(x, x + random.randrange(1,4), str(x))

unittest.main()