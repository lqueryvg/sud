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


# TODO CandidateSet should maybe be a member rather than a superclass.
# I'm not sure it seems natural for candidates to be "in" a cell.
class Cell(CandidateSet):
    def __init__(self, candidate_values, row=-1, col=-1):
        super(Cell, self).__init__(candidate_values)
        self.value = None
        self.name = "Cell{}{}".format(row, col)
        self.row = row
        self.col = col
        self.cell_value_set_listeners = []
        self.candidate_removed_listeners = []

    def add_cell_value_set_listener(self, lsnr):
        self.cell_value_set_listeners.append(lsnr)

    def add_cell_candidate_removed_listener(self, lsnr):
        self.candidate_removed_listeners.append(lsnr)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def get_value(self):
        return self.value

    def __repr__(self):
        return self.name

    def __str__(self):
        if self.value == None:
            return "-"
        else:
            return str(self.value)

    def set_value(self, value):
        if self.value is not None:
            return

        if value not in self:
            raise AssertionError("Value is not a candidate")

        self.value = value

        self.clear()    # remove all candidates
        for lsnr in self.cell_value_set_listeners:
            lsnr.cell_value_set_notification(self, value)

        # delete all listeners, since there can be no further changes
        # to this cell
        del self.cell_value_set_listeners[:]
        del self.candidate_removed_listeners[:]

    def remove_candidate(self, value):
        #print "in cell remove_candidate"
        super(Cell, self).remove_candidate(value)
        for lsnr in self.candidate_removed_listeners:
            #print "{} remove_candidate({}) calling listener {}".format(
            #        self.name, value, repr(lsnr))
            lsnr.cell_candidate_removed_notification(self, value)


class ConstraintGroup(object):
    def __init__(self, cells, puzzle=None, name=""):
        # Optionally point back to the puzzle
        self.puzzle = puzzle
        self.name = name

        self.cells = cells

        # listen to cells for value set
        for cell in cells:
            cell.add_cell_value_set_listener(self)

    def cell_value_set_notification(self, changed_cell, value):
        self.cells.remove(changed_cell)
        for cell in self.cells:
            # It's possible that an over-lapping contstraint
            # group has already deleted the candidate value
            # from this cell, so only remove candidate if
            # already there, otherwise we'll get a key error.
            if value in cell:
                if self.puzzle is not None:
                    self.puzzle.log_solution_step(
                            "RemoveCandidate {} from {} {}".format(
                                value, self.name, cell.name))
                try:
                    cell.remove_candidate(value)
                except SingleCandidate:
                    # list(my_set)[0] grabs any value from a set
                    cell.set_value(list(cell)[0])
                    if self.puzzle is not None:
                        self.puzzle.log_solution_step(
                                "SingleCandidate {} value is {}".format(
                                    cell.name, cell.value))

# When a value has been eliminated from the candidates of all except
# one cell in a constraint group.
class SinglePosition:
    def __init__(self, cgrp, puzzle=None):
        # Create a dictionary of possible cells
        # for each possible value in a constraint group.
        # I.e. a dictionary of lists of cells indexed by candidate values.
    
        #import pdb; pdb.set_trace()
        self.puzzle = puzzle
        self.possible_values = {}
        self.cgrp = cgrp
        self.name = cgrp.name
        for cell in cgrp.cells:
            if cell.value is not None:
                #import pdb; pdb.set_trace()
                raise AssertionError("Unexpected value in cgrp cell;"
                        " only cells without a value should be in a cgrp.")
            for candidate_value in cell:
                if candidate_value in self.possible_values:
                    self.possible_values.get(candidate_value).add(cell)
                else:
                    self.possible_values[candidate_value] = set([cell])

        
        for cell in cgrp.cells:
            cell.add_cell_candidate_removed_listener(self)
            cell.add_cell_value_set_listener(self)

        # If any values have only 1 possible cell, we have found some values
        for value in list(self.possible_values):
            possible_cells = self.possible_values[value]
            if len(possible_cells) == 1:
                self._found_value(iter(possible_cells).next(), value)

    def _found_value(self, cell, value):
        # we have found the last possible cell for this value
        if self.puzzle is not None:
            self.puzzle.log_solution_step(
                "SinglePosition for {} in {} {}".format(
                value, self.cgrp.name, cell.name))
        cell.set_value(value)

    def cell_value_set_notification(self, changed_cell, value):
        # no need to watch the value any more
        del self.possible_values[value]

    def cell_candidate_removed_notification(self, cell, value):
        # delete cell from set of possibilities for that value
        if value not in self.possible_values:
            return

        possible_cells = self.possible_values[value]
        possible_cells.discard(cell)
        if len(possible_cells) == 1:
            self._found_value(iter(possible_cells).next(), value)


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# The only candidates for a value in a box lie on a line (i.e. row or
# column), so the same value in other boxes on the same line can be
# eliminated.

class CandidateLines:

    def __init__(self, box_cgrp, puzzle=None):

        # Create an index for each box listing the possible rows & columns
        # within the box for each value not yet found.
        #
        # 1 rows{candidate_value} -> [ rownum1, rownum2, ...]
        # 2 cols{candidate_value} -> [ colnum1, colnum2, ...]
        #
        # rows{candidate_value}{rownum}{cells} = [ cells, peers ]
        # cols{candidate_value}{colnum} = count
        #
        # lines[value]['row'][rownum]['count'] = count
        # lines[value]['row'][rownum]['peers'] = set of cells
        # lines[value]['col'][colnum]['count'] = count
        # lines[value]['col'][colnum]['peers'] = set of cells
        #
        assert(puzzle is not None)
        
        self.puzzle = puzzle
        self.rows = {}      # TODO eliminate
        self.cols = {}      # TODO eliminate
        self.lines = AutoVivification()
        self.box_cgrp = box_cgrp
        self.name = box_cgrp.name

        for cell in box_cgrp.cells:
            if cell.value is not None:
                #import pdb; pdb.set_trace()
                raise AssertionError("Unexpected value in cgrp cell;"
                        " only cells without a value should be in a cgrp.")

            for cand in cell:
                row = self.lines[cand]['row'][cell.row]
                if 'count' not in row:
                    row['count'] = 0
                row['count'] += 1
                row['peers'] = self.box_cgrp.get_peers_in_row(cell.row)

                col = self.lines[cand]['row'][cell.col]
                if 'count' not in col:
                    col['count'] = 0
                col['count'] += 1
                col['peers'] = self.box_cgrp.get_peers_in_col(cell.col)

            #print self.name + " adding candidate lines listeners to " + repr(cell)
            cell.add_cell_candidate_removed_listener(self)
            cell.add_cell_value_set_listener(self)

        #import pdb; pdb.set_trace()

        # If any values have only 1 possible row or col within the box, we can
        # eliminate the value from other boxes in the same row or col.
        # lines[value]['row'][rownum]['count'] = count
        # lines[value]['row'][rownum]['peers'] = set of cells
        # lines[value]['col'][colnum]['count'] = count
        # lines[value]['col'][colnum]['peers'] = set of cells
        for cand in list(self.lines):
            for line_type in self.lines[cand]:
                for linenum in self.lines[cand][line_type]:
                    self._check_line(self.lines[cand][line_type], linenum, cand)

    def _check_row_for_candidate_line(self, value):
        if len(self.rows[value]) == 1:
            # Get line from which to eliminate this value.
            rownum = iter(self.rows[value]).next()
            print "CandidateLine {} eliminate {} from row {}".format(
                    self, value, rownum)
            del self.rows[value]
            for colnum in self.box_cgrp.get_cols_outside_this_box():
                self.puzzle.get_cell(rownum, colnum
                        ).remove_candidate(value)
        
    # TODO fix code duplication (with block above)
    def _check_col_for_candidate_line(self, value):
        if len(self.cols[value]) == 1:
            # Get line from which to eliminate this value.
            colnum = iter(self.cols[value]).next()
            print "CandidateLine {} eliminate {} from col {}".format(
                    self, value, rownum)
            del self.cols[value]
            for rownum in self.box_cgrp.get_rows_outside_this_box():
                self.puzzle.get_rc_cell(rownum, colnum
                        ).remove_candidate(value)

    def __repr__(self):
        return self.name

    def cell_value_set_notification(self, cell, value):
        del self.rows[value]
        del self.cols[value]

    def _check_line(self, lines, linenum, value):
        # If there is only one line in the box that
        # the value can be on, remove this value
        # from candidates of peers on same line.
        
        # Example:
        # lines[value]['row'][rownum]['count'] = count
        # lines[value]['row'][rownum]['peers'] = set of cells
        line = lines[linenum]
        if line['count'] == 1:
            for cell in line['peers']:
                cell.remove_candidate(value)
        del lines[linenum]


    def cell_candidate_removed_notification(self, cell, value):
        #import pdb; pdb.set_trace()
        # LOGIC FLAWED HERE
        # need a nested hash containing a count
        #self.rows[value].remove(cell.row)
        #self._check_row_for_candidate_line(value)
#
        raise AssertionError("not implemented yet")

        lines = self.lines[value]['row']
        lines[cell.row]['count'] -= 1
        self.check_line(lines, cell.row, value)

        lines = self.lines[value]['col']
        lines[cell.col]['count'] -= 1
        self.check_line(lines, cell.col, value)



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

    def get_cell(self, row, col):
        return self.grid[row][col]

    def get_row_cells(self, rownum):
        _row = []
        for colnum in range(self.numcols):
            _row.append(self.get_cell(rownum, colnum))
        return _row

    def get_col_cells(self, colnum):
        _col = []
        for rownum in range(self.numrows):
            _col.append(self.get_cell(rownum, colnum))
        return _col

    def get_box_cells(self, rownum, colnum):
        _box = []
        for boxrow in range(rownum, rownum + self.box_width):
            for boxcol in range(colnum, colnum + self.box_width):
                _box.append(self.get_cell(boxrow, boxcol))
        return _box

    def to_string(self):
        s = ""
        for rownum in range(self.numrows):
            if rownum > 0:
                s = s + "\n"
                if rownum % self.box_width == 0:
                    s = s + "\n"
            colnum = 0
            for cell in self.get_row_cells(rownum):
                if colnum > 0 and colnum % self.box_width == 0:
                    s = s + " "
                s = s + str(cell)
                colnum = colnum + 1
        return s


class Box(ConstraintGroup):
    def __init__(self, cells, puzzle=None, boxrow=0, boxcol=0):
        assert(puzzle is not None)
        super(Box, self).__init__(cells, puzzle,
                name = "Box" + str(boxrow) + str(boxcol)
                )
        self.boxrow = boxrow
        self.boxcol = boxcol

    def get_peers_in_col(self, col):
        allrows = range(self.puzzle.numrows)
        box_rows = range(self.boxrow, self.boxrow + self.puzzle.box_width)
        peers = []
        for row in set(allrows).difference(set(box_rows)):
            peers.append(self.puzzle.get_cell(row, col))
        return peers

    def get_peers_in_row(self, row):
        allcols = range(self.puzzle.numcols)
        box_cols = range(self.boxcol, self.boxcol + self.puzzle.box_width)
        peers = []
        for col in set(allcols).difference(set(box_cols)):
            peers.append(self.puzzle.get_cell(row, col))
        return peers


class Puzzle(Grid):

    def __init__(self, box_width):
        self.solution = []
        super(Puzzle, self).__init__(box_width)
        for rownum in range(self.numrows):
            for colnum in range(self.numcols):
                super(Puzzle, self).set_grid_rc_value(
                    rownum, colnum, Cell(range(1, self.numrows + 1),
                        row=rownum, col=colnum)
                )
        self._add_constraint_groups()

    def add_index():
        raise AssertionError("Not implemented yet")     # TODO

    def log_solution_step(self, string):
        #print "solution " + string
        self.solution.append(string)

    def _add_constraint_groups(self):
        self.cgrps = []     # all constraint groups
        self.box_cgrps = []     # just the boxes, for convenience
        for rownum in range(self.numrows):
            _row_cells = super(Puzzle, self).get_row_cells(rownum)
            self.cgrps.append(ConstraintGroup(_row_cells,
                puzzle=self, name="Row"+str(rownum)))

        for colnum in range(self.numcols):
            _col_cells = super(Puzzle, self).get_col_cells(colnum)
            self.cgrps.append(ConstraintGroup(
                        _col_cells, puzzle=self, name="Col"+str(colnum)))

        for boxrow in range(0, self.numrows, self.box_width):
            for boxcol in range(0, self.numcols, self.box_width):
                _box_cells = super(Puzzle, self).get_box_cells(boxrow, boxcol)
                box = Box(_box_cells, puzzle=self,
                        boxrow=boxrow, boxcol=boxcol)
                self.cgrps.append(box)
                self.box_cgrps.append(box)

#        for box in Grig.get_all_boxes():
#            cgrp = ConstraintGroup(s, self, name="Box"+str(box.coord))
#            self.cgrps.append(cgrp)
#            self.box_cgrps.append(cgrp)


    def add_SinglePosition(self):
        for cgrp in self.cgrps:
            dummy = SinglePosition(cgrp, puzzle=self)

    def add_CandidateLines(self):
        for box_cgrp in self.box_cgrps:
            dummy = CandidateLines(box_cgrp, puzzle=self)

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
                        cell = super(Puzzle, self).get_cell(_row, _col)
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
