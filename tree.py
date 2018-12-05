inf = float('inf')
ninf = float('-inf')

class IntervalTree:
    def __init__(self):
        self._root = IntervalNode()
        self._dict = {}

    def add(self, start, end, name):
        if not start < end:
            raise ValueError("The start of an interval must be smaller than its end")
        if name in self._dict:
            raise ValueError("Interval with same name already in tree")
        self._root = self._root.add(start, end, name)
        self._dict[name] = (start, end)

    def remove(self, name):
        if not name in self._dict:
            raise KeyError("Interval not in tree")
        start, end = self._dict[name]
        self._root = self._root.remove(name, start, end)
        del self._dict[name]

    def testPoint(self, point):
        return self._root.testPoint(point)

    def testRange(self, start, end):
        if not start < end:
            raise ValueError("The start of the range must be smaller than its end")
        return self._root.testRange(start, end)

    def getEndpoints(self, name):
        if not name in self._dict:
            raise KeyError("Interval not in tree")
        return self._dict[name]

    def clear(self):
        self._root = IntervalNode()

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

    @property
    def _isleaf(self):
        return self.boundary == None

    def _updateheight(self):
        if self._isleaf:
            return 0
        lheight = -1 if self.left._isleaf else self.left._height
        rheight = -1 if self.right._isleaf else self.right._height
        return 1 + max(lheight, rheight)

    # BALANCING FUNCTIONS

    def _rotateright(self):
        if self.left._isleaf:
            raise RotationError("Can't move a leaf node up")

        # Make copy of old intervals before clearing 
        oldrootintervals = set(self.intervals)
        newrootintervals = set(self.left.intervals)

        self.intervals.clear()
        self.left.intervals.clear()

        # Normal rotation
        newroot = self.left
        self.left = newroot.right
        newroot.right = self

        # The subinterval represented by each tree has changed
        newroot.min = self.min
        newroot.max = self.max
        self.min = newroot.boundary

        # Move around intervals 
        newroot.intervals = oldrootintervals

        newroot.left.intervals |= newrootintervals
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

        # Make a copy of the old intervals before clearing
        oldrootintervals = set(self.intervals)
        newrootintervals = set(self.right.intervals)

        self.intervals.clear()
        self.right.intervals.clear()

        # Normal rotation
        newroot = self.right
        self.right = newroot.left
        newroot.left = self

        # Update boundaries
        newroot.min = self.min
        newroot.max = self.max
        self.max = newroot.boundary

        # Move intervals around
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
    
    @property
    def _balance(self):
        rheight = self.right._height if self.right else 0
        lheight = self.left._height if self.left else 0
        return rheight - lheight

    def rebalance(self):
        # AVL algorithm
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

        newroot._height = newroot._updateheight()

        return newroot
    
    # ADDING AN INTERVAL

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

        # Balancing operations
        if not self._isleaf:
            self.left._height = self.left._updateheight()
            self.right._height = self.right._updateheight()
        self._height = self._updateheight()

        return self.rebalance()

    # REMOVAL FUNCTIONS

    @property
    def _emptychildren(self):
        llen = len(self.left.testRange(ninf, inf)) if self.left is not None else 0
        rlen = len(self.right.testRange(ninf, inf)) if self.left is not None else 0
        return llen == rlen == 0

    # This method checks if self is unnecessary and can be replaced with self.left:
    # Ex:
    #          7               5
    #        /   \            / \
    #       5    [a]   -->  [ ] [a]
    #      / \
    #    [ ] [a]
    @property
    def _canreplacewithleft(self):
        return len(self.intervals) == 0 and \
               not self._isleaf and \
               not self.left._isleaf and \
               self.right._isleaf and \
               self.right.intervals == self.left.right.intervals

    @property
    def _canreplacewithright(self):
        return len(self.intervals) == 0 and \
               not self._isleaf and \
               not self.right._isleaf and \
               self.left._isleaf and \
               self.right.left.intervals == self.left.intervals

    def remove(self, interval, start, end):
        if interval in self.intervals:
            self.intervals.remove(interval)
        elif not self._isleaf:
            if self.boundary >= start:
                self.left = self.left.remove(interval, start, end)
            if self.boundary <= end:
                self.right = self.right.remove(interval, start, end)

        # Removing unnecessary nodes
        if self._emptychildren:
            self.__init__(intervals = self.intervals, min = self.min, max = self.max)
        elif self._canreplacewithleft:
            newl = self.left.left
            newr = self.left.right
            self.__init__(self.left.boundary, self.left.intervals, min = self.min, max = self.max)
            self.left = newl
            self.right = newr
        elif self._canreplacewithright:
            newl = self.right.left
            newr = self.right.right
            self.__init__(self.right.boundary, self.right.intervals, min = self.min, max = self.max)
            self.left = newl
            self.right = newr

        # Balancing operations
        if not self._isleaf:
            self.left.height = self.left._updateheight()
            self.right.height = self.right._updateheight()
        self.height = self._updateheight()

        return self.rebalance()

    # QUERY FUNCTIONS

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