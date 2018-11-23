inf = float('inf')
ninf = float('-inf')

# TODO:
# Interval removal

class IntervalTree:
    def __init__(self):
        self._root = IntervalNode()

    def add(self, start, end, name):
        if start >= end:
            raise ValueError("The start of an interval must be smaller than its end")
        self._root.add(start, end, name)
        self._root = self._root.rebalance()

    def remove(self, name):
        self._root.remove(name)
        self._root = self._root.rebalance()

    def testPoint(self, point):
        return self._root.testPoint(point)

    def testRange(self, start, end):
        return self._root.testRange(start, end)

    def __repr__(self):
        return repr(self._root)

class RotationError(Exception):
    def __init__(self, str=""):
        Exception.__init__(self, str)

class IntervalNode:
    def __init__(self, boundary = None, intervals = (), min = ninf, max = inf):
        self.boundary = boundary
        self.intervals = set(intervals)
        self.left = IntervalNode(min = min, max = boundary) if boundary is not None else None
        self.right = IntervalNode(min = boundary, max = max) if boundary is not None else None
        self.min = min
        self.max = max
        self.height = 0
        
    def _nicerepr(self, n = 1):
        ret = (('B : ' + repr(self.boundary)) if not self._isleaf else "L") + ' : ' + repr(list(self.intervals))
        if self.left is not None:
            ret += '\n' + '  ' * n + '< ' + self.left._nicerepr(n + 1)
        if self.right is not None:
            ret += '\n' + '  ' * n + '> ' + self.right._nicerepr(n + 1)
        return ret

    def __repr__(self):
        return self._nicerepr()

    def _updateheight(self):
        if self._isleaf:
            return 0
        lheight = -1 if self.left._isleaf else self.left.height
        rheight = -1 if self.right._isleaf else self.right.height
        return 1 + max(lheight, rheight)

    def _rotateright(self):
        if self.left._isleaf:
            raise RotationError("Can't move a leaf node up")

        # The spans represented by the old and new roots change so you need to re-add all of the intervals in those two nodes
        # Make copy of old intervals before clearing 
        oldrootintervals = set(self.intervals)
        oldrootmin = self.min
        oldrootmax = self.max

        newrootintervals = set(self.left.intervals)
        newrootmin = self.left.min
        newrootmax = self.left.max

        self.intervals.clear()
        self.left.intervals.clear()

        newroot = self.left
        self.left = newroot.right
        newroot.right = self

        newroot.min = self.min
        newroot.max = self.max
        self.min = newroot.boundary

        for interval in oldrootintervals:
            newroot.add(oldrootmin, oldrootmax, interval)
        for interval in newrootintervals:
            newroot.add(newrootmin, newrootmax, interval)

        return newroot

    def _rotateleft(self):
        if self.right._isleaf:
            raise RotationError("Can't move a leaf node up")
        
        oldrootintervals = set(self.intervals)
        oldrootmin = self.min
        oldrootmax = self.max

        newrootintervals = set(self.left.intervals)
        newrootmin = self.left.min
        newrootmax = self.left.max

        self.intervals.clear()
        self.left.intervals.clear()

        newroot = self.right
        self.right = newroot.left
        newroot.left = self

        newroot.min = self.min
        newroot.max = self.max
        self.max = newroot.boundary

        for interval in oldrootintervals:
            newroot.add(oldrootmin, oldrootmax, interval)
        for interval in newrootintervals:
            newroot.add(newrootmin, newrootmax, interval)

        return newroot

    def rebalance(self):
        bal = self._balance
        if bal == -2:
            if self.left._balance > 0:
                self.left = self.left._rotateleft()
            newroot = self._rotateright()
        elif bal == 2:
            if self.right._balance < 0:
                self.right = self.right._rotateright()
            newroot = self._rotateleft()
        else:
            return self

        newroot.left.height = newroot.left._updateheight()
        newroot.left.height = newroot.right._updateheight()
        newroot.height = newroot._updateheight()

        return newroot

    @property
    def _isleaf(self):
        return self.boundary == None
    
    @property
    def _isemptynode(self):
        return len(self.intervals) == 0

    @property
    def _balance(self):
        rheight = self.right.height if self.right else 0
        lheight = self.left.height if self.left else 0
        return rheight - lheight

    # These two properties might not be needed based on how I end up handling removal
    # @property
    # def _isemptysubtree(self):
    #     if not self._isemptynode:
    #         return False
    #     if not self._isleaf:
    #         l = self.left._isemptysubtree if self.left is not None else True
    #         r = self.right._isemptysubtree if self.right is not None else True
    #         return l and r
    #     return True

    # @property
    # def _bothchildrenempty(self):
    #     l = self.left._isemptysubtree if self.left is not None else True
    #     r = self.right._isemptysubtree if self.right is not None else True
    #     return l and r

    def add(self, start, end, name):
        # This applies to all nodes
        if start <= self.min and end >= self.max:
            self.intervals.add(name)

        # Leaf cases
        elif self._isleaf:
            if start > self.min:
                self.boundary = start
                # If it's not a leaf I need to make sure it has both children
                self.left = IntervalNode(min = self.min, max = self.boundary)
                if end < self.max:
                    self.right = IntervalNode(end, min = self.boundary, max = self.max)
                    self.right.add(start, end, name)
                else:
                    self.right = IntervalNode(None, {name}, min = self.boundary, max = self.max)
            elif end < self.max:
                self.boundary = end
                self.left = IntervalNode(None, {name}, min = self.min, max = self.boundary)
                self.right = IntervalNode(min = self.boundary, max = self.max)
        
        # Non-leaf cases
        else:
            if end <= self.boundary:
                self.left.add(start, end, name)
            else: 
                self.right.add(start, end, name) 
            if start >= self.boundary:
                self.right.add(start, end, name)
            else:
                self.left.add(start, end, name)

        if self.left is not None:
            self.left.height = self.left._updateheight()
        if self.right is not None:
            self.right.height = self.right._updateheight()
        self.height = self._updateheight()

    # def remove(self, interval):
    #     # Does not work well
    #     if interval in self.intervals:
    #         self.intervals.remove(interval)
    #     elif not self._isleaf:
    #         self.left.remove(interval)
    #         self.right.remove(interval)

    #     if self._bothchildrenempty:
    #         self.__init__(intervals = self.intervals, min = self.min, max = self.max)

    #     self.height = self._updateheight()

    def testPoint(self, point):
        ret = set()
        if self.min <= point <= self.max:
            ret |= self.intervals
        if not self._isleaf:
            if point <= self.boundary:
                ret |= self.left.testPoint(point)
            if point >= self.boundary:
                ret |= self.right.testPoint(point)
        return ret 
        
    def testRange(self, start, end):
        ret = set()
        if self.max >= start and self.min <= end:
            ret |= self.intervals
        if not self._isleaf:
            if start <= self.boundary:
                ret |= self.left.testRange(start, end)
            if self.boundary <= end:
                ret |= self.right.testRange(start, end)
        return ret