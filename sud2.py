#!/usr/bin/env python2

import collections
import sets

class LastCandidate(Exception):
    pass

import sets

#class CandidateSet(collections.Set):
class CandidateSet(sets.Set):
    # Like a Set but raises exceptions when:
    # - trying to remove final element
    # - only 1 element remains after removing an element (i.e.
    #   we have found the only remaining possible candidate)
    # - trying to initialise with 1 or zero candidates
    
    # See ListBasedSet example in
    # https://docs.python.org/2/library/collections.html
    # for inheritance formalities.
    def __iter__(self):
        return iter(self.elements)
    def __contains__(self, value):
        return value in self.elements
    def __len__(self):
        return len(self.elements)

    # Specialised code.
    def __init__(self, iterable):
        if len(iterable) <= 1:
            raise Exception("need >1 element to init candidate set")
        super(CandidateSet, self).__init__(iterable)
        #super(CandidateSet, self).add(iterable)
        #collections.Set.__init__(self, iterable)
#        self.elements = lst = []
#        for value in iterable:
#            if value not in lst:
#                lst.append(value)

    def remove(self, value):
        #if len(self.elements) == 1:
        if len(self) == 1:
            raise Exception("attempt to remove final candidate")
        self.elements.remove(value)
        if len(self.elements) == 1:
            raise LastCandidate


class Cell(CandidateSet):
    def add_constraint_group(self, grp):
        pass
 
