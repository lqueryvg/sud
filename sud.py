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

cell_possibles = []    # [col][row] = set of possible values for a cell

box_possibles = []      # [box_col][box_row][value] = set of possible
                       #        coords for value in box
row_possibles = []      # [row][value] = set of possible columns for value in row
col_possibles = []      # [col][value] = set of possible rows for value in column
result_grid = []       # [col][row] = value; value is '-' if unknown

known_cells_count = 0

def init():
    for _col in range(0, 9):
        #print "_col = ", _col
        result_grid.append([])
        cell_possibles.append([])
        for _row in range(0, 9):
            #print "_row = ", _row
            cell_possibles[_col].append(set([1,2,3,4,5,6,7,8,9]))
            result_grid[_col].append("-")
    # init boxes
    for _col in range(0, 3):
        box_possibles.append([])        # add empty column
        for _row in range(0, 3):
            box_possibles[_col].append([])        # add empty n list
            for _value in range(0, 9):
                box_possibles[_col][_row].append(set([]))
                for _box_col in range(_col*3, (_col*3)+3):
                    for _box_row in range(_row*3, (_row*3)+3):
                        box_possibles[_col][_row][_value].add((_box_col, _box_row));
    # init rows
    for _row in range(0,9):
        row_possibles.append([])        # add empty row
        for _value in range(0, 9):
            row_possibles[_row].append(set([]))        # add empty n set
            for _col in range(0, 9):
                row_possibles[_row][_value].add(_col)
    # init columns
    for _col in range(0,9):
        col_possibles.append([])        # add empty column
        for _value in range(0, 9):
            col_possibles[_col].append(set([]))        # add empty n set
            for _row in range(0, 9):
                col_possibles[_col][_value].add(_row)

def remove_cell_candidate(col, y, value):
    # Called when it is certain that a cell can't contain a value.

    # Remove its value or its coords from the various "possibles" data
    # structures. This in turn can recurse when only one cell possibility
    # is found.

    # TODO need verbose function
    #print "remove_cell_candidate(%d, %d) %d" % (col, y, value)

    # Cell
    # Remove value from set of possibilities for that cell.
    cell = cell_possibles[col][y]
    if (value in cell and len(cell) > 1):
        cell.remove(value)
        if (len(cell) == 1):    # found last possible value for cell
            onlyValue = cell.pop()
            print "cellfind %d at (%d, %d)" % (onlyValue, col, y)
            cell.add(onlyValue)
            set_cell(col, y, onlyValue)

    # Box
    # Remove coord from set of possibilities for that value in containing box.
    (_box_col, _box_row) = (col/3, y/3)
    coords = box_possibles[_box_col][_box_row][value-1]
    # todo: EXPLAIN 1
    if ((col, y) in coords and len(coords) > 1):
        coords.remove((col, y))
        if (len(coords) == 1):
            onlyCoord = coords.pop()
            coords.add(onlyCoord)
            print "boxfind value %d at" % value, onlyCoord
            set_cell(onlyCoord[0], onlyCoord[1], value)

    # Row
    # Remove col from row for that value.
    xValues = row_possibles[y][value-1]
    if (col in xValues and len(xValues) > 1):
        xValues.remove(col)
        if (len(xValues) == 1):
            onlyX = xValues.pop()
            xValues.add(onlyX)
            print "rowfind value %d (%d, %d)" % (value, onlyX, y)
            set_cell(onlyX, y, value)

    # Column
    # Remove row from column for that value.
    yValues = col_possibles[col][value-1]
    # TODO need verbose function
    #print "col %d remove %d from" % (col, y), yValues
    if (y in yValues and len(yValues) > 1):
        yValues.remove(y)
        if (len(yValues) == 1):
            onlyY = yValues.pop()
            yValues.add(onlyY)
            print "colfind value %d (%d, %d)" % (value, col, onlyY)
            set_cell(col, onlyY, value)

def reduce_possibles(col, row, known_value):
    # Given known value for a cell, reduce possibilities
    # elsewhere (row, column and box)
    #print "reduce(%d, %d) %d" % (col, row, known_value)
    
    # For completeness, we have to reduce the various possibility
    # sets down to just one value, since this value is known and
    # is the only possible value.
    cell_possibles[col][row] = set([known_value])
    box_possibles[col/3][row/3][known_value-1] = set([(col, row)])
    row_possibles[row][known_value-1] = set([col])
    col_possibles[col][known_value-1] = set([row])
    
    # Cell
    #print "reduce cell..."
    for _value in range(0,9):
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
    for _row in range(0, 9):
        if (_row != row):
            remove_cell_candidate(col, _row, known_value)
    
    # Row
    #print "reduce row..."
    for _col in range(0, 9):
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
    reduce_possibles(_col, _row, know_value)
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
    for _row in range(0, 9):
        if (_row == 3 or _row == 6):
            print ""
        for _col in range(0, 9):
            if (_col == 3 or _col == 6):
                sys.stdout.write(" ")
            sys.stdout.write("%c" % str(result_grid[_col][_row]))
        print ""

def print_cell_possibles():
    print "Cell possibles:"
    for _row in range(0, 9):
        for _col in range(0, 9):
            poss = cell_possibles[_col][_row]
            if (len(poss) > 1):
                print "cell (%d, %d) = " % (_col, _row), poss

def print_box_possibles():
    print "Box possibles:"
    for _col in range(0, 3):
        for _row in range(0, 3):
            print "box(%d, %d):" % (_col, _row)
            # print by value
            for _value in range(1, 10):
                poss = box_possibles[_col][_row][_value-1]
                if (len(poss) > 1):
                    print "  value %d = " % _value, poss
            # print by coord
            for _box_col in range(0,3):
                for _box_row in range(0,3):
                    cellposs = cell_possibles[_col*3 + _box_col][_row*3 + _box_row]
                    if (len(cellposs) > 1):
                        print "  cell (%d, %d) = " % (_box_col, _box_row), cellposs

def print_row_possibles():
    print "Row possibles:"
    for _row in range(0, 9):
        print "row %d:" % _row
        for _value in range(1, 10):
            poss = row_possibles[_row][_value-1]
            if (len(poss) > 1):
                print "  value %d =" % _value, poss

def print_col_possibles():
    print "Col possibles:"
    for _col in range(0, 9):
        print "col %d:" % _col
        for _value in range(1, 10):
            poss = col_possibles[_col][_value-1]
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
    for _col in range(0, 9):        # for each column
        #print "col %d:" % _col
        dict = {}
        for _value in range(1, 10):        # for each value
            poss = frozenset(col_possibles[_col][_value-1])
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
                    for _candidate in cell_possibles[_col][_row]:
                        if _candidate not in dict[poss]:
                            print "      eliminate %d at (%d, %d)" % \
                                (_candidate, _col, _row)
                            eliminate_cell_candidate(_col, _row, _candidate)
                            break

    print "Search for row pairs..."
    for _row in range(0, 9):        # for each row
        #print "row %d:" % _row
        dict = {}
        for _value in range(1, 10):        # for each value
            poss = frozenset(row_possibles[_row][_value-1])
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
                    for _candidate in cell_possibles[_col][_row]:
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
    print_cell_possibles()
    print_box_possibles()
    print_row_possibles()
    print_col_possibles()
