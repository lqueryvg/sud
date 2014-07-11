#!/usr/bin/env python2


class SingleCandidate(Exception):
    # Only one candidate remains after remove.
    pass


class RemoveOnlyCandidate(Exception):
    # An attempt to remove the only candidate
    pass


class AtLeastTwoCandidateValuesRequired(Exception):
    # Need at least two or more candidate values to create a CandidateSet
    pass


class CandidateSet(set):
    # Like a Set but raises exceptions when:
    # - trying to remove final element
    # - only 1 element remains after removing an element (i.e.
    #   we have found the only remaining possible candidate)
    # - trying to initialise with less than 2 candidate values

    # Specialised code.
    def __init__(self, candidate_values):
        if len(candidate_values) < 2:
            raise AtLeastTwoCandidateValuesRequired
        super(CandidateSet, self).__init__(candidate_values)

    def remove_candidate(self, value):
        if len(self) == 1:
            raise RemoveOnlyCandidate
        super(CandidateSet, self).remove(value)
        if len(self) == 1:
            raise SingleCandidate


class CellAlreadySet(Exception):
    pass


class ValueIsNotACandidate(Exception):
    pass


class Cell(CandidateSet):
    def __init__(self, candidate_values):
        # self.candidates = CandidateSet(candidate_values)
        super(Cell, self).__init__(candidate_values)
        self.value = None
        self.constraint_groups = []

    def add_constraint_group(self, grp):
        self.constraint_groups.append(grp)

    def get_value(self):
        return self.value

    def set_value(self, value):
        if self.value is not None:
            raise CellAlreadySet
        # if value not in self.candidates:
        if value not in self:
            raise ValueIsNotACandidate
        self.value = value
        # self.candidates.clear()    # remove all candidates
        self.clear()    # remove all candidates
        for constraint_grp in self.constraint_groups:
            constraint_grp.notify_cell_changed(self, value)
        del self.constraint_groups[:]


class ConstraintGroup:
    def __init__(self, cells):
        self.cells = cells

        # Point each cell back to this constraint group
        for cell in cells:
            cell.add_constraint_group(self)

    def notify_cell_changed(self, changed_cell, new_value):
        self.cells.remove(changed_cell)
        for cell in self.cells:
            try:
                # cell.candidates.remove(new_value)
                cell.remove_candidate(new_value)
            except SingleCandidate:
                # list(my_set)[0] grabs any value from set
                cell.set_value(list(cell)[0])
