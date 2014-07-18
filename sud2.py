#!/usr/bin/env python2


class SingleCandidate(Exception):
    # Only one candidate remains after remove.
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
            raise AssertionError("At least two candidates required")
        super(CandidateSet, self).__init__(candidate_values)

    def remove_candidate(self, value):
        if len(self) == 1:
            raise AssertionError("Attempt to remove final candidate")
        super(CandidateSet, self).remove(value)

        if len(self) == 1:
            raise SingleCandidate


class Cell(CandidateSet):
    def __init__(self, candidate_values, name=""):
        super(Cell, self).__init__(candidate_values)
        self.value = None
        self.name = name
        self.value_change_listeners = []
        self.candidate_removed_listeners = []

    def add_cell_value_set_listener(self, lsnr):
        self.value_change_listeners.append(lsnr)

    def add_cell_candidate_removed_listener(self, lsnr):
        self.candidate_removed_listeners.append(lsnr)

    def get_value(self):
        return self.value

    def set_value(self, value):
        if self.value is not None:
            return

        if value not in self:
            raise AssertionError("Value is not a candidate")

        self.value = value

        self.clear()    # remove all candidates
        for lsnr in self.value_change_listeners:
            lsnr.notify_cell_value_set(self, value)
        del self.value_change_listeners[:]

    def remove_candidate(self, value):
        super(Cell, self).remove_candidate(value)
        for lsnr in self.candidate_removed_listeners:
            lsnr.notify_cell_candidate_removed(self, value)


class ConstraintGroup:
    def __init__(self, cells, puzzle=None, name=""):
        # Optionally point back to the puzzle
        self.puzzle = puzzle
        self.name = name

        self.cells = cells

        # Point each cell back to this constraint group
        for cell in cells:
            cell.add_cell_value_set_listener(self)

    def notify_cell_value_set(self, cell_set, value):
        self.cells.remove(cell_set)
        for cell in self.cells:
            # It's possible that an over-lapping contstraint
            # group has already deleted the candidate value
            # from this cell, so only remove candidate if
            # already there, otherwise we'll get a key error.
            if value in cell:
                if self.puzzle is not None:
                    self.puzzle.logit(
                            "{} RemoveCandidate {} from {}".format(
                                self.name, value, cell.name))
                try:
                    cell.remove_candidate(value)
                except SingleCandidate:
                    # list(my_set)[0] grabs any value from a set
                    cell.set_value(list(cell)[0])
                    if self.puzzle is not None:
                        self.puzzle.logit(
                                "SingleCandidate Cell {} value is {}".format(
                                    cell.name, cell.value))

    def notify_cell_candidate_removed(self, value):
        # Constraint group is not interested in candidate removals.
        pass

class SinglePositionIndex:
    def __init__(self, cgrp):
        # Create a dictionary of possible cells
        # for each possible value in a constraint group.
        # I.e. a dictionary of lists of cells indexed by candidate values.
    
        self.index = {}
        for cell in cgrp.cells:
            if cell.value is not None:
                for candidate_value in cell:
                    if candidate_value in self.index:
                        self.index.get(candidate_value).append(cell)
                    else:
                        self.index[candidate_value] = [cell]

        # self.value_cells =
        for cell in cgrp.cells:
            cell.add_cell_candidate_removed_listener(self)
            cell.add_cell_value_set_listener(self)

    def notify_cell_value_set(self, cell_set, value):
            raise AssertionError("Not implemented yet")     # TODO

    def notify_cell_candidate_removed(self, cell, value):
            raise AssertionError("Not implemented yet")     # TODO



# Note: Grid knows nothing about Cells.  Grid implements a grid of values (not
# to be confused with Cell values) and provides a way of accessing them
# individually or as groups (rows, columns or boxes).  It just so happens that
# when used by the Puzzle, the grid values are references to Cell objects.

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
    def set_grid_rc_value(self, row, col, value):
        self.grid[row][col] = value

    def get_grid_rc_value(self, row, col):
        return self.grid[row][col]

    def get_row(self, rownum):
        _row = []
        for colnum in range(self.numcols):
            _row.append(self.get_grid_rc_value(rownum, colnum))
        return _row

    def get_col(self, colnum):
        _col = []
        for rownum in range(self.numrows):
            _col.append(self.get_grid_rc_value(rownum, colnum))
        return _col

    def get_box(self, rownum, colnum):
        _box = []
        for boxrow in range(rownum, rownum + self.box_width):
            for boxcol in range(colnum, colnum + self.box_width):
                _box.append(self.get_grid_rc_value(boxrow, boxcol))
        return _box


class Puzzle(Grid):

    def add_index():
        raise AssertionError("Not implemented yet")     # TODO

    def logit(self, string):
        #print "log " + string
        self.log.append(string)

    def _add_constraint_groups(self):
        for rownum in range(self.numrows):
            _row = super(Puzzle, self).get_row(rownum)
            ConstraintGroup(_row, self, name="Row"+str(rownum))

        for colnum in range(self.numcols):
            _col = super(Puzzle, self).get_col(colnum)
            ConstraintGroup(_col, self, name="Col"+str(colnum))

        boxnum = 0
        for boxrow in range(0, self.numrows, self.box_width):
            for boxcol in range(0, self.numcols, self.box_width):
                _box = super(Puzzle, self).get_box(boxrow, boxcol)
                ConstraintGroup(_box, self, name="Box"+str(boxnum))
                boxnum = boxnum + 1

    def __init__(self, box_width):
        self.log = []
        super(Puzzle, self).__init__(box_width)
        for rownum in range(self.numrows):
            for colnum in range(self.numcols):
                super(Puzzle, self).set_grid_rc_value(
                    rownum, colnum, Cell(range(1, self.numrows + 1),
                        name="Cell{}{}".format(rownum, colnum))
                )
        self._add_constraint_groups()

    def load_from_iterable(self, iterable):
        _row = 0
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
                #import pdb; pdb.set_trace()
                raise PuzzleParseError(
                    ('Row {}: expect {} words (one per box); '
                    + 'found {}.').format(
                        _row, self.box_width, _num_box_words
                ))


            _col = 0
            for _word in _box_words:
                if len(_word) != self.box_width:
                    raise PuzzleParseError(
                        ('Row {}: text = "{}", length of word "{}" is {}, '
                            + 'but must match box width {}').format(
                            _row, _line, _word, len(_word), self.box_width
                    ))

                import struct
                _values = struct.unpack('c' * self.box_width, _word)

                for _v in _values:
                    if (_v != '-'):
                        cell = super(Puzzle, self).get_grid_rc_value(_row, _col)
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
