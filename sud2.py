#!/usr/bin/env python2

import logging
import pprint

class Metrics:
    """

    Initial attempt at counting solver "misses", where an attempt is being made
    to set or remove values which have already been set/removed, due to
    overlapping solvers.

    If these numbers can be reduced, it should make the solvers more efficient.

    """
    def __init__(self):
        self.metrics = {}

    def inc(self, name):
        """
        This must be called at appropriate points in the code.
        """
        if name not in self.metrics:
            self.metrics[name] = 1
        else:
            self.metrics[name] += 1

    def to_string(self):
        from pprint import pformat
        return pformat(self.metrics)

metrics = Metrics()
    
class SingleCandidate(Exception):
    # Only one candidate remains after remove.
    pass

class CandidateSet(set):
    """
    Like a Set but raises exceptions when:
    - trying to remove final element
    - only 1 element remains after removing an element (i.e.
      we have found the only remaining possible candidate)
    - trying to initialise with less than 2 candidate values
    """

    def __init__(self, candidate_values):
        super(CandidateSet, self).__init__(candidate_values)

    def remove_candidate(self, value):
        #import pdb; pdb.set_trace()
        if len(self) == 1:
            raise AssertionError("Attempt to remove final candidate")
        super(CandidateSet, self).remove(value)

        if len(self) == 1:
            raise SingleCandidate


class Cell():
    def __init__(self, candidate_values, row=-1, col=-1):
        self.value = None
        self.name = "Cell{}{}".format(row, col)
        self.row = row
        self.col = col
        self.candidate_set = CandidateSet(candidate_values)
        self.cell_value_set_listeners = []
        self.candidate_removed_listeners = []

    def set_candidates(self, candidate_values):
        """
        Bypasses all checks and propagation.
        Intended for testing.
        """
        self.candidate_set.clear()
        self.candidate_set = CandidateSet(candidate_values)

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
            return "."
        else:
            return str(self.value)

    def set_value(self, value):
        logging.info("%s set_value(%s) called", self.name, value)
        #import pdb; pdb.set_trace()
        if self.value is not None:
            metrics.inc('Cell.already_set')
            logging.info("%s set_value(%s) already set", self.name, value)
            return

        #if value not in self:
        if value not in self.candidate_set:
            raise AssertionError("Value is not a candidate")

        self.value = value

        self.candidate_set.clear()    # remove all candidates
        for lsnr in self.cell_value_set_listeners:
            logging.info(
            "{} set_value({}) calling listener {}".format(
                    self.name, value, repr(lsnr))
            )
            lsnr.on_value_set(self, value)

        # delete all listeners, since there can
        # be no further changes to this cell
        del self.cell_value_set_listeners[:]
        del self.candidate_removed_listeners[:]

    def remove_candidate(self, value):
        logging.debug(
            "Cell remove_candidate() %s from %s", value, self.name)

        try:
            self.candidate_set.remove_candidate(value)
        except SingleCandidate:
            self.set_value(list(self.candidate_set)[0])  # grab any

        for lsnr in self.candidate_removed_listeners:
            logging.debug(
            "{} remove_candidate({}) calling listener {}".format(
                    self.name, value, repr(lsnr))
            )
            lsnr.on_candidate_removed(self, value)


class CellGroup(object):
    """
    Just a grouping of cells with an optional name.
    """
    def __init__(self, cells=[], name="CellGroup"):
        self.name = name
        self.cells = cells

    def __repr__(self):
        return self.name


class UniqueConstraints(object):
    """
    Ensures that values are not repeated for cells in a group.
    If the group already contains repeats, then an Exception
    is raised with a list of violations.
    """

    @staticmethod
    def add_to_puzzle(puzzle=None):

        assert(puzzle is not None)

        for cell_group in puzzle.cell_groups:
            # TODO worry about GC
            dummy = UniqueConstraints(
                cell_group,
                puzzle=puzzle,
                name = cell_group.name + '.UniqueConstraints'
            )

    def __init__(self, cell_group, puzzle=None, name=None):
        # Optionally point back to the puzzle
        self.puzzle = puzzle
        if name is None:
            self.name = cell_group.name + '.UniqueConstraints'
        else:
            self.name = name

        self.cells = list(cell_group.cells)      # store a copy

        # Check for violations.
        # A list of violations will be raised in a single exception.
        cell_for_value = dict()
        violations = []
        for cell in self.cells:
            value = cell.value
            if value is not None:
                if value in cell_for_value:
                    # Violation found.
                    other_cell = cell_for_value[value]
                    violations.append([value, cell, other_cell])
                else:
                    cell_for_value[value] = cell

        if len(violations) > 0:
            raise Exception(self.name + " broken", violations)

        # listen to cells for value set
        for cell in self.cells:
            cell.add_cell_value_set_listener(self)

    def on_value_set(self, cell, value):
        self.cells.remove(cell)
        for neighbor in self.cells:
            # It's possible that an over-lapping contstraint
            # group has already deleted the candidate value
            # from this neighbor, so only remove candidate if
            # already there, otherwise we'll get a key error.
            if value in neighbor.candidate_set:
                if self.puzzle is not None:
                    self.puzzle.log_solution_step(
                            "RemoveCandidate {} from {} {}".format(
                                value, self.name, neighbor.name))
                #try:
                neighbor.remove_candidate(value)
                #except SingleCandidate:
                #    neighbor.set_value(
                #        list(neighbor.candidate_set)[0]  # grab any
                #    )
                #    if self.puzzle is not None:
                #        self.puzzle.log_solution_step(
                #                "SingleCandidate {} value is {}".format(
                #                    neighbor.name, neighbor.value))
            else:
                metrics.inc('UniqueConstraints.candidate_already_removed')

    def __repr__(self):
        return self.name

class SinglePosition:
    """
    Detects when a value has been eliminated from the candidates of all but
    one cell in a cell group; then the cell value is known.
    """
    @staticmethod
    def add_to_puzzle(puzzle=None):
        """
        Note: not an instance method.
        Creates lots of 
        """
        assert(puzzle is not None);

        for cell_group in puzzle.cell_groups:
            # TODO wonder about GC
            dummy = SinglePosition(cell_group, puzzle=puzzle)

    def __init__(self, cell_group, puzzle=None):
        """
        Create a dictionary of possible cells
        for each possible value in a constraint group.
        I.e. a dictionary of lists of cells indexed by candidate values.
        """
    
        #import pdb; pdb.set_trace()
        self.puzzle = puzzle
        self.possible_cells_by_value = {}
        self.cells = list(cell_group.cells)   # make a copy
        self.name = cell_group.name + ".SinglePosition"
        for cell in self.cells:
            #for candidate_value in cell:
            for candidate_value in cell.candidate_set:
                if candidate_value in self.possible_cells_by_value:
                    self.possible_cells_by_value.get(candidate_value).add(cell)
                else:
                    self.possible_cells_by_value[candidate_value] = set([cell])

        
        for cell in self.cells:
            cell.add_cell_candidate_removed_listener(self)
            cell.add_cell_value_set_listener(self)

        # If any values have only 1 possible cell, we have found some values
        for value in list(self.possible_cells_by_value):
            #import pdb; pdb.set_trace()
            if value not in self.possible_cells_by_value:
                metrics.inc('SinglePosition.miss0')
                continue
            possible_cells = self.possible_cells_by_value[value]
            if len(possible_cells) == 1:
                self._found_value(iter(possible_cells).next(), value)

    def __repr__(self):
        return self.name

    def _found_value(self, cell, value):
        # we have found the last possible cell for this value
        if self.puzzle is not None:
            self.puzzle.log_solution_step(
                "SinglePosition for {} in {} {}".format(
                value, self.name, cell.name))
        cell.set_value(value)

    def on_value_set(self, changed_cell, value):
        # no need to watch the value any more
        if value in self.possible_cells_by_value:
            del self.possible_cells_by_value[value]
        else:
            metrics.inc('SinglePosition.miss1')

    def on_candidate_removed(self, cell, value):
        # delete cell from set of possibilities for that value
        if value not in self.possible_cells_by_value:
            metrics.inc('SinglePosition.miss2')
            return

        possible_cells = self.possible_cells_by_value[value]
        possible_cells.discard(cell)
        if len(possible_cells) == 1:
            metrics.inc('SinglePosition.found')
            self._found_value(iter(possible_cells).next(), value)


class CandidateLines:
    """
    If the only candidates for a value in a box lie on a line (i.e.
    a row or column) within that box, eliminates the value from
    candidates of cells in other boxes on the same line.
    """
    
    @staticmethod
    def add_to_puzzle(puzzle=None):

        logging.info("CandidateLines.add_to_puzzle() called")
        assert(puzzle is not None)
        for box_group in puzzle.boxes:
            # TODO wonder about GC
            dummy = CandidateLines(box_group, puzzle=puzzle)

    def __repr__(self):
        return "CandidateLines." + self.name

    def __init__(self, box_cell_group, puzzle=None):
        """
        For every value not yet known in the box, index the list of rows and
        cols the value can be on.  For each of those rows/cols, store the list
        of cells within the box the value can be in.
        """
        assert(puzzle is not None)
        
        # Internal index is a nested dict and looks like this.
        #
        # index[cand]['row'][rownum]['cells'] = set of cells
        # index[cand]['row'][rownum]['peers'] = set of cells
        # index[cand]['col'][colnum]['cells'] = set of cells
        # index[cand]['col'][colnum]['peers'] = set of cells
        #
        # For example, to show that the candidate value 1
        # can be on row 0 in cells (0,0), (0,1) and (0,2)
        # the data structure might look like this (only
        # the top row is depicted).

        # +--+    +---+     +-+                             
        # |1 |--> |row|---> |0|---> (Cell00, Cell01, Cell02)
        # +--+    +---+     +-+                             
        # |2 |    |col|     |1|                             
        # +--+    +---+     +-+                             
        # |3 |              |2|                             
        # +--+              +-+                             
        # |. |                                              
        # |. |                                              
        # +--+                                              

        
        self.puzzle = puzzle
        self.index = {}
        self.box_cell_group = box_cell_group
        self.name = box_cell_group.name
        logging.info("in CandidateLines.__init__(), self.name = %s", self.name)

        for cell in box_cell_group.cells:
            logging.info(
                    "in CandidateLines.__init__(), cell = %s[%s]",
                    repr(cell),
                    "".join(str(x) for x in sorted(cell.candidate_set))
            )

            #import pdb; pdb.set_trace()
            for cand in cell.candidate_set:
                if cand not in self.index:
                    # Create empty row and col dicts.
                    self.index[cand] = dict(row=dict(), col=dict())

                def store_peers(line_num, line_type, get_peers_fn):
                    lines = self.index[cand][line_type]
                    if line_num not in lines:
                        lines[line_num] = {
                            'cells': set(),
                            'peers': get_peers_fn(line_num)
                            }
                    lines[line_num]['cells'].add(cell)

                store_peers(cell.row, 'row', box_cell_group.get_peers_in_row)
                store_peers(cell.col, 'col', box_cell_group.get_peers_in_col)

            cell.add_cell_candidate_removed_listener(self)
            cell.add_cell_value_set_listener(self)

        logging.debug(
            "in CandidateLines.__init__(), index =\n%s",
            pprint.pformat(self.index)
        )

        # If any values have only 1 possible row or col within the box,
        # eliminate them from other boxes in the same row or col.
        #import pdb; pdb.set_trace()
        for cand in list(self.index):
            # use list() here because we might del items as we go
            if cand not in self.index:
                # WOW, could have been deleted by something else
                continue

            for line_type in list(self.index[cand]):
                if cand not in self.index:
                    continue
                else:
                    metrics.inc('CandidateLines.miss.cand_deleted1')

                if len(self.index[cand][line_type]) == 1:
                    #import pdb; pdb.set_trace()
                    linenum, line = self.index[cand][line_type].popitem()
                    for cell in line['peers']:
                        if cand in cell.candidate_set:
                            cell.remove_candidate(cand)
                            metrics.inc('CandidateLines.remove_cand1')

                    if cand in self.index:
                        del self.index[cand][line_type]
                    else:
                        metrics.inc('CandidateLines.miss.cand_deleted2')

    def on_value_set(self, cell, value):
        """
        Once the position of a value is known, delete
        it from the index, and also delete the cell from the lists
        of cells within the index.
        Each time the cell is deleted, use check_line() to
        see if a CandidateLine condition has been found.
        """

        logging.info("CandidateLines.on_value_set()")
        logging.info("  %s cell=%s, value=%s", self.name, repr(cell), value)

        del self.index[value]

        logging.info("  index =\n%s", pprint.pformat(self.index))

        #import pdb; pdb.set_trace()
        # Delete this cell from the index.
        for cand_value in list(self.index):
            def del_from_index(line_type, line_num):
                if cand_value not in self.index:
                    metrics.inc('CandidateLines.miss.cand3')
                    return

                if line_type not in self.index[cand_value]:
                    metrics.inc('CandidateLines.miss.line_type_deleted')
                    return

                lines = self.index[cand_value][line_type]

                if line_num not in lines:
                    # assume overlapping condition deleted it
                    metrics.inc('CandidateLines.miss.line_deleted')
                    return
                
                #    import pdb; pdb.set_trace()

                if cell in lines[line_num]['cells']:
                    lines[line_num]['cells'].remove(cell)
                    self.check_line(cand_value, line_type, line_num)
            del_from_index('row', cell.row)
            del_from_index('col', cell.col)


        logging.info(
            "in CandidateLines.on_value_set(),"
            "modified index =\n%s",
            pprint.pformat(self.index)
        )

    def check_line(self, value, line_type, line_num):
        """
        If there is only one line within the box that a value
        can be on, remove the value
        from the candidates of all peers on the line.
        """

        logging.info("  check_line %s %s for value %s",
                line_type, line_num, value)
        if len(self.index[value][line_type][line_num]['cells']) == 0:
            logging.info("    no more cells for value")

            del self.index[value][line_type][line_num]

            if len(self.index[value][line_type]) == 1:
                linenum, line = self.index[value][line_type].popitem()
                logging.info("    delete %s %s", line_type, linenum)
                logging.info("    removing peers")
                #import pdb; pdb.set_trace()
                for peer_cell in line['peers']:
                    if value in peer_cell.candidate_set:
                        peer_cell.remove_candidate(value)
                        metrics.inc('CandidateLines.remove_cand1')
                if value in self.index:
                    del self.index[value][line_type]
                else:
                    metrics.inc('CandidateLines.miss.cand4')

    def on_candidate_removed(self, cell, value):
        """
        Remove the changed cell from the set of cells on the same
        row and column for the candiate value that has been removed.
        """

        logging.info("CandidateLines.on_candidate_removed()")
        logging.info("  %s cell=%s, value=%s", self.name, repr(cell), value)

        if value in self.index:

            logging.info("  value is in index")
            def _remove_from_line(line_type, line_num):
                if value not in self.index: return  # TODO count these
                if line_type in self.index[value]:
                    lines = self.index[value][line_type]
                    if line_num in lines:
                        logging.info(
                            "  removing from cells for %s %s",
                            line_type, line_num
                        )
                        lines[line_num]['cells'].remove(cell)
                        self.check_line(value, line_type, line_num)

            _remove_from_line('col', cell.col)
            _remove_from_line('row', cell.row)


class Grid(object):
    """
    Implements a grid of values (not to be confused with Cell values) and
    provides a way of accessing them individually or as groups (rows, columns
    or boxes).  When used by Puzzle, the grid values are references to Cell
    objects.
    """

    def __init__(self, box_width):
        """
        Internally a list of lists, as [row][col].
        Coords start at 0.
        """

        self.grid = []
        self.numcols = self.numrows = box_width ** 2
        self.box_width = box_width
        for rownum in range(self.numrows):
            row = []
            for colnum in range(self.numcols):
                row.append(None)
            self.grid.append(row)

    def set_grid_rc_value(self, row, col, value):
        """
        Index by row then column.
        """
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
                #import pdb; pdb.set_trace()
                _box.append(self.get_cell(boxrow, boxcol))
        return _box

    def to_string(self):
        s = ""
        for rownum in range(self.numrows):
            if rownum > 0:
                s = s + "\n"
                if rownum % self.box_width == 0:
                    t = '+'.join(["-"*10*self.box_width]*self.box_width) + "\n"
                    l = list(t)
                    l[0] = '#'
                    s += ''.join(l)
            colnum = 0
            for cell in self.get_row_cells(rownum):
                if colnum > 0 and colnum % self.box_width == 0:
                    s = s + "|"
                if cell.value is None:
                    s = s + ''.join(str(x) for x in sorted(
                        cell.candidate_set)
                    ).center(10, " ")
                else:
                    s = s + str(cell.value).center(10, " ")
                colnum = colnum + 1
        return s

    def is_equal_to(self, other):
        for row in range(self.numrows):
            for col in range(self.numcols):
                my_cell = self.get_cell(row, col)
                other_cell = other.get_cell(row, col)
                if my_cell.value != other_cell.value or \
                        my_cell.candidate_set != other_cell.candidate_set:
                    return False
        return True


class Box(CellGroup):
    """
    Remembers the row and column of the top left cell
    in the box and adds utility functions to get
    the 'peer' cells of a row or column.
    'Peers' are cells in the specified line but outside
    of this box.
    """
    def __init__(self, cells, puzzle=None, boxrow=0, boxcol=0):
        """
        boxrow and boxcol address the top left cell in the box.
        The box name will encode the same.
        """
        assert(puzzle is not None)
        super(Box, self).__init__(
            cells=cells, 
            name = "Box" + str(boxrow) + str(boxcol)
        )
        self.puzzle = puzzle
        self.name ="Box" + str(boxrow) + str(boxcol)
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
        self.solution_steps = []
        super(Puzzle, self).__init__(box_width)
        for rownum in range(self.numrows):
            for colnum in range(self.numcols):
                super(Puzzle, self).set_grid_rc_value(
                    rownum, colnum, Cell([], row=rownum, col=colnum)
                )
        self.init_all_candidates()
        self.cell_groups = []   # all cell groups
        self.boxes = []         # just the boxes, for convenience
        self.init_groups()

    def init_all_candidates(self):
        for rownum in range(self.numrows):
            for colnum in range(self.numcols):
                super(Puzzle, self).get_cell(rownum, colnum).set_candidates(
                        map(str, range(1, self.numrows + 1))
                )

    def log_solution_step(self, string):
        self.solution_steps.append(string)

    def init_groups(self):
        for rownum in range(self.numrows):
            _row_cells = super(Puzzle, self).get_row_cells(rownum)
            self.cell_groups.append(CellGroup(_row_cells,
                name="Row"+str(rownum)))

        for colnum in range(self.numcols):
            _col_cells = super(Puzzle, self).get_col_cells(colnum)
            self.cell_groups.append(CellGroup(
                        _col_cells, name="Col"+str(colnum)))

        for boxrow in range(0, self.numrows, self.box_width):
            for boxcol in range(0, self.numcols, self.box_width):
                _box_cells = super(Puzzle, self).get_box_cells(boxrow, boxcol)
                box = Box(_box_cells, puzzle=self,
                        boxrow=boxrow, boxcol=boxcol)
                self.cell_groups.append(box)
                self.boxes.append(box)

    def load_from_iterable(self, iterable):
        """
        Each line is split into words.
        Each word represents a row of a box and since
        all boxes should be the same width, each word
        should be the same number of characters.
        """
        _row = 0
        for _line in iterable:
            import re

            # support script style comments with '#'
            re.sub(r"#.*$", '', _line)  # strip them

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
                        ('Row {}: unexpected number of words; expect {} words '
                        '(one per box); found {}.').format(
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
                    cell = super(Puzzle, self).get_cell(_row, _col)
                    if _v in cell.candidate_set:
                        metrics.inc('initially_given')
                        cell.set_value(_v)
                    metrics.inc('total_cells')
                    _col += 1

            _row = _row + 1
        return

    def load_from_string(self, string):
        self.load_from_iterable(iter(string.splitlines()))

    def load_from_file(self, pathname):
        self.load_from_iterable(open(pathname))

    def load_candidates_from_iterable(self, iterable):
        """
        Each line is split on whitespace into words.
        Each word represents a cells candates (any order but no spaces).
        Any char in a word which is not in the valid range for a candidate
        (e.g. 1-9) is ignored.

        TODO have single load routine that supports candidates or values
        """
        _row = 0
        _valid_candidate_values = set(map(str, range(1, self.numrows + 1)))
        for _line in iterable:
            import re

            # support script style comments with '#'
            _line = re.sub(r'#.*$', '', _line)  # strip them
            #import pdb; pdb.set_trace()
            _line = re.sub(r'\|', '', _line)  # delete any decorative pipes

            _cell_words = _line.split()
            _num_cells = len(_cell_words)

            if _num_cells == 0:
                continue        # skip blank lines

            if (_row >= self.numrows):
                raise PuzzleParseError(
                        'Row {}: too many rows, expected {}.'.format(
                            _row, self.numrows)
                        )

            if _num_cells != self.box_width**2:
                #import pdb; pdb.set_trace()
                raise PuzzleParseError(
                    ('Row {}: unexpected number of words; expect {} (one per cell); '
                    + 'found {}.\nline is {}').format(
                        _row, self.box_width**2, _num_cells, _line
                ))

            _col = 0
            #import pdb; pdb.set_trace()
            for _word in _cell_words:
                cell = super(Puzzle, self).get_cell(_row, _col)
                if _word == '.':
                    pass
                    # ignore
                else:
                    _word_candidates = list(_word)
                    if set(_word_candidates).issubset(_valid_candidate_values):
                        if len(_word_candidates) == 1:
                            cell.set_value(_word_candidates[0])
                        else:
                            cell.set_candidates(_word_candidates)
                    else:
                        #import pdb; pdb.set_trace()
                        raise PuzzleParseError(
                                'Row {}: invalid candidate(s) found in word\n'
                                'word: {}\nline: {}\nvalid candidates are: {}'
                                .format(
                                    _row, _word, _line,
                                    ''.join(_valid_candidate_values)
                                )
                        )
                _col += + 1

            _row = _row + 1
        return

    def load_candidates_from_string(self, string):
        self.load_candidates_from_iterable(iter(string.splitlines()))

    def load_candidates_from_file(self, pathname):
        self.load_candidates_from_iterable(open(pathname))


class PuzzleParseError(Exception):
    pass

def main():

    import argparse

    parser = argparse.ArgumentParser(description='Solve Sudoku puzzle.')
    parser.add_argument('filename', nargs=1)
    parser.add_argument(
        '--boxwidth', default=3,
        help='box width in cells')

    args = parser.parse_args()
    filename = args.filename[0]
    puzzle = Puzzle(args.boxwidth)

    # TODO why can't UniqueConstraints be added after loading puzzle ?
    UniqueConstraints.add_to_puzzle(puzzle)
    puzzle.load_from_file(filename)
    SinglePosition.add_to_puzzle(puzzle)
    CandidateLines.add_to_puzzle(puzzle)
    print puzzle.to_string()
    print metrics.to_string()

if __name__ == '__main__':
    main()

# The End
# vim:foldmethod=indent:foldnestmax=2
