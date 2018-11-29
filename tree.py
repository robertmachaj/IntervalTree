inf = float('inf')
ninf = float('-inf')

# TODO:
# Interval removal

class IntervalTree:
    def __init__(self):
        self._root = IntervalNode()

    def add(self, start, end, name):
        if not (start < end):
            raise ValueError("The start of an interval must be smaller than its end")
        self._root = self._root.add(start, end, name)

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
        self._height = 0
        
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
        lheight = -1 if self.left._isleaf else self.left._height
        rheight = -1 if self.right._isleaf else self.right._height
        return 1 + max(lheight, rheight)

    def _rotateright(self):
        if self.left._isleaf:
            raise RotationError("Can't move a leaf node up")

        # The spans represented by the old and new roots change so you need to re-add all of the intervals in those two nodes
        # Make copy of old intervals before clearing 
        oldrootintervals = set(self.intervals)
        newrootintervals = set(self.left.intervals)

        self.intervals.clear()
        self.left.intervals.clear()

        newroot = self.left
        self.left = newroot.right
        newroot.right = self

        newroot.min = self.min
        newroot.max = self.max
        self.min = newroot.boundary

        newroot.intervals = oldrootintervals

        newroot.left.intervals |= newrootintervals
        # self is oldroot
        self.left.intervals |= newrootintervals

        # Join up any intervals that are in both children of oldroot
        both = self.left.intervals & self.right.intervals
        self.intervals |= both
        self.left.intervals -= both
        self.right.intervals -= both

        self._height = self._updateheight()
        newroot._height = newroot._updateheight()
        return newroot

    def _rotateleft(self):
        if self.right._isleaf:
            raise RotationError("Can't move a leaf node up")
        
        oldrootintervals = set(self.intervals)
        newrootintervals = set(self.right.intervals)

        self.intervals.clear()
        self.right.intervals.clear()

        newroot = self.right
        self.right = newroot.left
        newroot.left = self

        newroot.min = self.min
        newroot.max = self.max
        self.max = newroot.boundary

        newroot.intervals = oldrootintervals

        newroot.right.intervals |= newrootintervals
        self.right.intervals |= newrootintervals

        both = self.left.intervals & self.right.intervals
        self.intervals |= both
        self.left.intervals -= both
        self.right.intervals -= both

        self._height = self._updateheight()
        newroot._height = newroot._updateheight()
        return newroot

    def rebalance(self):
        bal = self._balance
        if bal < -1:
            if self.left._balance > 0 and not self.left.right._isleaf:
                self.left = self.left._rotateleft()
            newroot = self._rotateright()
        elif bal > 1:
            if self.right._balance < 0 and not self.right.left._isleaf:
                self.right = self.right._rotateright()
            newroot = self._rotateleft()
        else:
            return self

        newroot.left._height = newroot.left._updateheight()
        newroot.right._height = newroot.right._updateheight()
        newroot._height = newroot._updateheight()

        return newroot

    @property
    def _isleaf(self):
        return self.boundary == None
    
    @property
    def _isemptynode(self):
        return len(self.intervals) == 0

    @property
    def _balance(self):
        rheight = self.right._height if self.right else 0
        lheight = self.left._height if self.left else 0
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
                    self.right = self.right.add(start, end, name)
                else:
                    self.right = IntervalNode(None, {name}, min = self.boundary, max = self.max)
            elif end < self.max:
                self.boundary = end
                self.left = IntervalNode(None, {name}, min = self.min, max = self.boundary)
                self.right = IntervalNode(min = self.boundary, max = self.max)

        # Non-leaf cases
        else:
            if start < self.boundary or end <= self.boundary:
                self.left = self.left.add(start, end, name)
            if start >= self.boundary or end > self.boundary:
                self.right = self.right.add(start, end, name)

        if not self._isleaf:
            self.left._height = self.left._updateheight()
            self.right._height = self.right._updateheight()
        self._height = self._updateheight()

        return self.rebalance()

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