#!/usr/bin/env python2

class LastCandidate(Exception):
    pass

class CandidateSet(set):
    # Like a Set but raises exceptions when:
    # - trying to remove final element
    # - only 1 element remains after removing an element (i.e.
    #   we have found the only remaining possible candidate)
    # - trying to initialise with 1 or zero candidates
    

    # Specialised code.
    def __init__(self, iterable):
        if len(iterable) <= 1:
            raise Exception("need >1 element to init candidate set")
        super(CandidateSet, self).__init__(iterable)

    def remove(self, value):
        if len(self) == 1:
            raise Exception("attempt to remove final candidate")
        super(CandidateSet, self).remove(value)
        if len(self) == 1:
            raise LastCandidate

class Cell(CandidateSet):
    def add_constraint_group(self, grp):
        pass
 
