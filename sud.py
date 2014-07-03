#!/usr/bin/env python2

import os,re,struct,sys

import argparse
parser = argparse.ArgumentParser(description='Solve Sudoku puzzle.')
parser.add_argument('filename', nargs=1)
args = parser.parse_args()
filename = args.filename[0]

# Example input file format:
# -6- 3-- 8-4
# 537 -9- ---
# -4- --6 3-7
#
# -9- -51 238
# --- --- ---
# 713 62- -4-
#
# 3-6 4-- -1-
# --- -6- 523
# 1-2 --9 -8-
#
# Empty rows (no characters at all) are skipped.
# Boxes in each row are separated by a single space.
# Unknown cells contain a hyphen "-".

# Notes:
#
# - Cells are arranged in a 9x9 grid.
# - Each cell value is a number from 1 to 9 or '-' if unknown.
# - Cell row and column indexes are in the range 0 to 8.
# - The grid is divided into nine 3x3 boxes of cells.
# - Box row and column indexes (both of a box itself and
#   of the cells within the box) are in the range 0 to 2.
# - Multi-dimensional arrays representing grids are indexed
#   by column then row, so as to resemble [x][y] coordinates.
# - Cell possibilities are implemented as sets for easy inclusion testing,
#   intersection, union, etc.
#

cell_candidates = []   # [col][row] = set of possible values for a cell

box_candidates = []    # [box_col][box_row][value] = set of possible
                       #        coords for value in box
row_candidates = []    # [row][value] = set of possible cols for value in row
col_candidates = []    # [col][value] = set of possible rows for value in col
result_grid = []       # [col][row] = value; value is '-' if unknown

all_values = range(1, 10)   # all cell values, i.e. 1 - 9
all_indices = range(0, 9)   # all row, col or value indices, i.e. 0 - 8

known_cells_count = 0

def init():
    for _col in all_indices:
        #print "_col = ", _col
        result_grid.append([])
        cell_candidates.append([])
        for _row in all_indices:
            #print "_row = ", _row
            cell_candidates[_col].append(set(all_values))
            result_grid[_col].append("-")
    # init boxes
    for _col in range(0, 3):
        box_candidates.append([])        # add empty column
        for _row in range(0, 3):
            box_candidates[_col].append([])        # add empty n list
            for _value in all_indices:
                box_candidates[_col][_row].append(set([]))
                for _box_col in range(_col*3, (_col*3)+3):
                    for _box_row in range(_row*3, (_row*3)+3):
                        box_candidates[_col][_row][_value].add(
                                (_box_col, _box_row)
                        );

    # init rows
    for _row in all_indices:
        row_candidates.append([])        # add empty row
        for _value in all_indices:
            row_candidates[_row].append(set([]))        # add empty n set
            for _col in all_indices:
                row_candidates[_row][_value].add(_col)

    # init columns
    for _col in all_indices:
        col_candidates.append([])        # add empty column
        for _value in all_indices:
            col_candidates[_col].append(set([]))        # add empty n set
            for _row in all_indices:
                col_candidates[_col][_value].add(_row)

def remove_cell_candidate(col, row, eliminated_value):
    # Called when it is certain that a cell doesn't contain a value.
    # Remove its value or its coords from the various "candidates" data
    # structures. This in turn can recurse when only one possibility
    # remains in any of those structures.

    # TODO need verbose function
    #print "remove_cell_candidate(%d, %d) %d" % (col, row, eliminated_value)

    # Cell
    # Remove eliminated_value from set of possibilities for that cell.
    cell = cell_candidates[col][row]
    if (eliminated_value in cell and len(cell) > 1):
        cell.remove(eliminated_value)
        if (len(cell) == 1):    # found last possible value for cell
            only_remaining_value = cell.pop()
            print "found cell value %d at (%d, %d)" % (only_remaining_value, col, row)
            cell.add(only_remaining_value)
            set_cell(col, row, only_remaining_value)

    # Box
    # Remove coord from set of possibilities for the eliminated value in
    # containing box.
    (_box_col, _box_row) = (col/3, row/3)
    coords = box_candidates[_box_col][_box_row][eliminated_value-1]
    if ((col, row) in coords and len(coords) > 1):
        coords.remove((col, row))
        if (len(coords) == 1):
            onlyCoord = coords.pop()
            coords.add(onlyCoord)
            print "found box value %d at" % eliminated_value, onlyCoord
            set_cell(onlyCoord[0], onlyCoord[1], eliminated_value)

    # Row
    # Remove col from row for the eliminated value.
    col_indices = row_candidates[row][eliminated_value-1]
    if (col in col_indices and len(col_indices) > 1):
        col_indices.remove(col)
        if (len(col_indices) == 1):
            only_col = col_indices.pop()
            col_indices.add(only_col)
            print "found row value %d (%d, %d)" % (eliminated_value, only_col, row)
            set_cell(only_col, row, eliminated_value)

    # Column
    # Remove row from column for the eliminated value.
    row_indices = col_candidates[col][eliminated_value-1]
    # TODO need verbose function
    #print "col %d remove %d from" % (col, row), row_indices
    if (row in row_indices and len(row_indices) > 1):
        row_indices.remove(row)
        if (len(row_indices) == 1):
            only_row = row_indices.pop()
            row_indices.add(only_row)
            print "found col value %d (%d, %d)" % (eliminated_value, col, only_row)
            set_cell(col, only_row, eliminated_value)

def reduce_candidates(col, row, known_value):
    # Given known value for a cell, reduce possibilities
    # elsewhere (row, column and box)
    #print "reduce(%d, %d) %d" % (col, row, known_value)
    
    # For completeness, we have to reduce the various possibility
    # sets down to just one value, since this value is known and
    # is the only possible value.
    cell_candidates[col][row] = set([known_value])
    box_candidates[col/3][row/3][known_value-1] = set([(col, row)])
    row_candidates[row][known_value-1] = set([col])
    col_candidates[col][known_value-1] = set([row])
    
    # Cell
    #print "reduce cell..."
    for _value in all_indices:
        if (_value+1 != known_value):
            remove_cell_candidate(col, row, _value+1)
    
    # Box
    #print "reduce box..."
    (_col, _row) = ((col/3)*3, (row/3)*3) # find top left of box
    #print "  reduceBox (_col, _row) = (%d, %d)" % (_col, _row)
    for _coli in range(_col, _col+3):
        for _rowi in range(_row, _row+3):
            if (_coli != col or _rowi != row):
                #print "    reduceBox cell is (%d, %d)" % (_coli, _rowi)
                remove_cell_candidate(_coli, _rowi, known_value)
    
    # Column
    #print "reduce column..."
    for _row in all_indices:
        if (_row != row):
            remove_cell_candidate(col, _row, known_value)
    
    # Row
    #print "reduce row..."
    for _col in all_indices:
        if (_col != col):
            remove_cell_candidate(_col, row, known_value)

def set_cell(_col, _row, know_value):
    # Call this whenever a cell value is certain.
    # It kicks off the process of elimination, which may recurse back into
    # this function if another cell value is found.

    #print "Setting cell(%d, %d), current value = %s" % (_col, _row, result_grid[_col][_row])

    # Return if cell already set
    if result_grid[_col][_row] != '-':
        return

    result_grid[_col][_row] = know_value
    reduce_candidates(_col, _row, know_value)
    global known_cells_count
    known_cells_count += 1
    # TODO: raise exception here if solved

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


# Output functions
def print_result():
    for _row in all_indices:
        if (_row == 3 or _row == 6):
            print ""
        for _col in all_indices:
            if (_col == 3 or _col == 6):
                sys.stdout.write(" ")
            sys.stdout.write("%c" % str(result_grid[_col][_row]))
        print ""

def print_cell_candidates():
    print "Cell candidates:"
    for _row in all_indices:
        for _col in all_indices:
            poss = cell_candidates[_col][_row]
            if (len(poss) > 1):
                print "cell (%d, %d) = " % (_col, _row), poss

def print_box_candidates():
    print "Box candidates:"
    for _col in range(0, 3):
        for _row in range(0, 3):
            print "box(%d, %d):" % (_col, _row)
            # print by value
            for _value in all_values:
                poss = box_candidates[_col][_row][_value-1]
                if (len(poss) > 1):
                    print "  value %d = " % _value, poss
            # print by coord
            for _box_col in range(0,3):
                for _box_row in range(0,3):
                    cellposs = cell_candidates[_col*3 + _box_col][_row*3 + _box_row]
                    if (len(cellposs) > 1):
                        print "  cell (%d, %d) = " % (_box_col, _box_row), cellposs

def print_row_candidates():
    print "Row candidates:"
    for _row in all_indices:
        print "row %d:" % _row
        for _value in all_values:
            poss = row_candidates[_row][_value-1]
            if (len(poss) > 1):
                print "  value %d =" % _value, poss

def print_col_candidates():
    print "Col candidates:"
    for _col in all_indices:
        print "col %d:" % _col
        for _value in all_values:
            poss = col_candidates[_col][_value-1]
            if (len(poss) > 1):
                print "  value %d =" % _value, poss

# End of print output functions

def solve():
    print "Solving..."
    # This is where we need to implement fancy stuff to do a bit more
    # clever detection.
    # E.g. "matched cell groups"
    # Example, candidates in a column...
    # Row   Candidates
    #    1.    46                        46
    #    2.    1469                     19 (remove 46)
    #    3.    68            ->            68
    #    4.    48                        48
    #    5.    14689                     19 (remove 468)
    # In above, 19 appear in rows 2 & 5 only, so remove other candidates from
    # rows 2 & 5.
    # For each value in remaining candidates, we already have a set of
    # locations where it occurs.
    #
    #    1 = {    2,       5 }
    #    4 = { 1, 2,    4, 5 }
    #    6 = { 1, 2, 3,    5 }
    #    8 = {       3, 4, 5 }
    #    9 = {    2,       5 }
    #
    # Construct hash indexed by set of locations, containing list of candidate
    # values. For above example hash will look like this...
    #
    #    {    2,       5 } = (1, 9)
    #    { 1, 2,    4, 5 } = (4)
    #    { 1, 2, 3,    5 } = (6)
    #    {       3, 4, 5 } = (8)
    #
    # Immediately we can see that one element has a set with two locations
    # and a list of 2 candidates. Therefore, for these two locations we
    # can remove all other candidates.
    #
    print "Search for column pairs..."
    for _col in all_indices:        # for each column
        #print "col %d:" % _col
        dict = {}
        for _value in all_values:        # for each value
            poss = frozenset(col_candidates[_col][_value-1])
            if (poss in dict):
                dict[poss].append(_value)
            else:
                dict[poss] = [_value]
        for poss in dict:
            if len(poss) == 2 and len(dict[poss]) == 2:
                print "  col", _col, ":", poss, "=", dict[poss]
                for _row in poss:
                    eliminateList = []
                    # for each of these cells, eliminate other candidates
                    for _candidate in cell_candidates[_col][_row]:
                        if _candidate not in dict[poss]:
                            print "      eliminate %d at (%d, %d)" % \
                                (_candidate, _col, _row)
                            eliminate_cell_candidate(_col, _row, _candidate)
                            break

    print "Search for row pairs..."
    for _row in all_indices:        # for each row
        #print "row %d:" % _row
        dict = {}
        for _value in all_values:        # for each value
            poss = frozenset(row_candidates[_row][_value-1])
            if (poss in dict):
                dict[poss].append(_value)
            else:
                dict[poss] = [_value]
        for poss in dict:
            if len(poss) == 2 and len(dict[poss]) == 2:
                print "  row", _row, ":", poss, "=", dict[poss]
                for _col in poss:
                    eliminateList = []
                    # for each of these cells, eliminate other candidates
                    for _candidate in cell_candidates[_col][_row]:
                        if _candidate not in dict[poss]:
                            print "      eliminate %d at (%d, %d)" % \
                                (_candidate, _col, _row)
                            eliminate_cell_candidate(_col, _row, _candidate)
                            break

    print "Search for box pairs..."

init()
loadfile(filename)
print "Cells solved = %d/%d" % (known_cells_count, (9*9))
if (known_cells_count != (9*9)):
    solve()
    print "Cells solved = %d/%d" % (known_cells_count, (9*9))
    solve()
    print "Cells solved = %d/%d" % (known_cells_count, (9*9))
    solve()
    print "Cells solved = %d/%d" % (known_cells_count, (9*9))
print_result()
if (known_cells_count == (9*9)):
    print "Solved!"
else:
    print "Not solved."
    print_cell_candidates()
    print_box_candidates()
    print_row_candidates()
    print_col_candidates()
