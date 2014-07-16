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
        super(Cell, self).__init__(candidate_values)
        self.value = None
        self.value_change_listeners = []
        self.candidate_removed_listeners = []

    def add_value_change_listener(self, lsnr):
        self.value_change_listeners.append(lsnr)

    def add_candidate_change_listener(self, lsnr):
        self.candidate_removed_listeners.append(lsnr)

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
        for lsnr in self.value_change_listeners:
            lsnr.notify_cell_value_changed(self, value)
        del self.value_change_listeners[:]

    def remove_candidate(self, value):
        super(Cell, self).remove_candidate(value)
        for lsnr in self.candidate_removed_listeners:
            lsnr.notify_cell_candidate_removed(self, value)


class ConstraintGroup:
    def __init__(self, cells):
        self.cells = cells

        # Point each cell back to this constraint group
        for cell in cells:
            cell.add_value_change_listener(self)

    def notify_cell_value_changed(self, changed_cell, new_value):
        self.cells.remove(changed_cell)
        for cell in self.cells:
            try:
                cell.remove_candidate(new_value)
            except SingleCandidate:
                # list(my_set)[0] grabs any value from set
                cell.set_value(list(cell)[0])

class SinglePositionIndex:
    def __init__(self, cgrp):
        # Create a dictionary of possible cells
        # for each possible value in a constraint group.
        # I.e. a dictionary of lists of cells indexed by candidate values.
        raise AssertionError("Not implemented yet")     # TODO
        #self.value_cells = 
        for cell in cgrp.cells:
            cell.add_candidate_change_listener(self)

class Grid(object):
    def __init__(self, numrows, numcols):

        # list of lists, as [row][col]
        # coords start at 0
        self.grid = [[]]   
        for rownum in range(numrows):
            column = []
            for colnum in range(numcols):
                column.append(None)
            self.grid.append(column)

    # index by row then column
    def set_rc_cell(self, row, col, value):
        self.grid[row][col] = value

    # index by x then y (column then row)
    def set_xy_cell(self, x, y, value):
        self.grid[y][x] = value


class Puzzle(Grid):
    def __init__(self):
        super(Puzzle, self).__init__(9, 9)
        for x in range(9):
            for y in range(9):
                self.set_xy_cell = Cell(range(1,10))

    # TODO add load from file


def loadfile(pathname):

    # Empty rows are skipped.
    # One line per row.
    # One character per column with
    _file = open(pathname)
    _row = 0
    for _line in _file:
        if re.search(r"^$", _line):
            continue
        if (_row > 8):
            print "Too many rows (" + str(_row) + " > 8)"
            sys.exit(1)
        _values = struct.unpack("cccxcccxcccx", _line);
        _col = 0
        # TODO: detect errors on input
        for _v in _values:
            #print "_v = %s" % _v
            if (_v != '-'):
                set_cell(_col,_row,int(_v))
            _col = _col + 1
        _row = _row + 1
    return
    
# The End
