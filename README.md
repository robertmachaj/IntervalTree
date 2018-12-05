# CSE 2050 Honors Project: Interval Tree

This is an implementation of an interval tree in Python. It has the following public interface:

- [x] `add(start, end, name)`: Add an interval to the tree
- [x] `remove(interval)`: Remove an interval from the tree
- [x] `clear()`: Clear all nodes and intervals from the tree
- [x] `getEndpoints(name)`: Returns a tuple of the start and endpoints to an interval
- [x] `testPoint(point)`: Returns a set of any intervals which overlap with a given point
- [x] `testRange(start, end)`: Returns any intervals that overlap with the given range (both endpoints inclusive)

Each node in the tree represents an interval or span. The top node represents the span from negative infinity to infinity. Each non-leaf node also has a boundary. This boundary defines the spans of its children. If an interval is stored in a particular node, it means that it includes that span. An interval can stretch across multiple spans. All endpoints in this tree are inclusive.

The purpose of the interval tree is to allow queries on intervals in logarithmic time. To be able to do this, the tree balances itself using the AVL algorithm as shown in the book.
