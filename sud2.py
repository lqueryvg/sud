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

        if value not in self:
            raise ValueIsNotACandidate

        self.value = value

        self.clear()    # remove all candidates
        for lsnr in self.value_change_listeners:
            lsnr.notify_cell_set(self, value)
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

    def notify_cell_set(self, cell_set, value):
        self.cells.remove(cell_set)
        for cell in self.cells:
            # It's possible that an over-lapping contstraint
            # group has already deleted the candidate value
            # from this cell, so only remove candidate if
            # already there, otherwise we'll get a key error.
            if value in cell:
                try:
                    cell.remove_candidate(value)
                except SingleCandidate:
                    # list(my_set)[0] grabs any value from a set
                    cell.set_value(list(cell)[0])


class SinglePositionIndex:
    def __init__(self, cgrp):
        # Create a dictionary of possible cells
        # for each possible value in a constraint group.
        # I.e. a dictionary of lists of cells indexed by candidate values.
        raise AssertionError("Not implemented yet")     # TODO
        # self.value_cells =
        for cell in cgrp.cells:
            cell.add_candidate_change_listener(self)


class Grid(object):
    def __init__(self, box_width):

        # list of lists, as [row][col]
        # coords start at 0
        self.grid = []
        self.numcols = self.numrows = box_width ** 2
        self.box_width = box_width
        for rownum in range(self.numrows):
            row = []
            for colnum in range(self.numcols):
                row.append(None)
            self.grid.append(row)

    # index by row then column
    def set_rc_cell(self, row, col, value):
        self.grid[row][col] = value

    # index by x then y (column then row)
    def set_xy_cell(self, x, y, value):
        self.grid[y][x] = value

    def get_rc_cell(self, row, col):
        return self.grid[row][col]

    def get_row(self, rownum):
        _row = []
        for colnum in range(self.numcols):
            _row.append(self.get_rc_cell(rownum, colnum))
        return _row

    def get_col(self, colnum):
        _col = []
        for rownum in range(self.numrows):
            _col.append(self.get_rc_cell(rownum, colnum))
        return _col

    def get_box(self, rownum, colnum):
        _box = []
        for boxrow in range(rownum, rownum + self.box_width):
            for boxcol in range(colnum, colnum + self.box_width):
                _box.append(self.get_rc_cell(boxrow, boxcol))
        return _box


class Puzzle(Grid):

    def _add_constraint_groups(self):
        for rownum in range(self.numrows):
            _row = super(Puzzle, self).get_row(rownum)
            dummy = ConstraintGroup(_row)

        for colnum in range(self.numcols):
            _col = super(Puzzle, self).get_col(colnum)
            dummy = ConstraintGroup(_col)

        for boxrow in range(0, self.numrows, self.box_width):
            for boxcol in range(0, self.numcols, self.box_width):
                _box = super(Puzzle, self).get_box(boxrow, boxcol)
                dummy = ConstraintGroup(_box)

    def __init__(self, box_width):
        super(Puzzle, self).__init__(box_width)
        for rownum in range(self.numrows):
            for colnum in range(self.numcols):
                super(Puzzle, self).set_rc_cell(
                    rownum, colnum, Cell(range(1, self.numrows + 1))
                )
        self._add_constraint_groups()

    def load_from_iterable(self, iterable):
        _row = 0
        _box_width = 0
        for _line in iterable:
            import re

            # support script style comments with '#'
            re.sub(r"#.*$", '', _line)  # strip them

            # Each line is split into words.
            # Each word represents a row of a box and since
            # all boxes should be the same width, each word
            # should be the same number of characters.
            _box_words = _line.split()
            _num_box_words = len(_box_words)

            if _num_box_words == 0:
                continue        # skip blank lines

            if (_row >= self.numrows):
                raise PuzzleParseError(
                        'Row {}: too many rows, expected {}.'.format(
                            _row, self.numrows)
                        )

            if _num_box_words != self.box_width:
#                import pdb; pdb.set_trace()
                raise PuzzleParseError(
                    ('Row {}: expect {} words (one per box); '
                    + 'found {}.').format(
                        _row, self.box_width, _num_box_words
                ))


            for _word in _box_words:
                if len(_word) != self.box_width:
                    raise PuzzleParseError(
                        ('Row {}: text = "{}", length of word "{}" is {}, '
                            + 'but must match box width {}').format(
                            _row, _line, _word, len(_word), self.box_width
                    ))

                import struct
                _values = struct.unpack('c' * self.box_width, _word)
                _col = 0

                for _v in _values:
                    #print "_v = %s" % _v
                    if (_v != '-'):
                        cell = super(Puzzle, self).get_rc_cell(_row, _col)
                        #import pdb; pdb.set_trace()
                        cell.set_value(int(_v))
                    _col = _col + 1

            _row = _row + 1
        return

    def load_from_string(self, string):
        self.load_from_iterable(iter(string.splitlines()))

    def load_from_file(self, pathname):
        self.load_from_iterable(open(pathname))


class PuzzleParseError(Exception):
    pass


# The End
# vim:foldmethod=indent:foldnestmax=2
