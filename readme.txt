Constraint Group

    My own generic term for a row, column or box.
    The 9 cells in a constraint group are "tied together"
    and constrained in that they collectively must contain
    each of the numbers 1 to 9 without repeats.

    When a cell value is set, the value can be removed
    from the candidates sets of all cells which
    are in the cell's same constraint groups.

Sudoku Solving Techniques

I will use the same names and techniques found here:

http://www.sudokuoftheday.com/techniques

Single Position

    When there's only one possible position (cell) in a constraint group
    that can contain a value.

    TODO:
    Finding these in a constraint group requires creating an index
    of sets of cell positions for each candidate value.

Single Candidate

    When there is only one possible candidate remaining for a particular cell.

Candidate Lines (TODO)

    If candidates for a value in a box line on a single row or column
    then the value must lie within that box and no other boxes in
    the same row or column (respectively).

    Hence the value can be eliminated from cells in the same row
    or column (respectively) in other boxes.

    This could be acheived by creating an index for each box
    which lists the possible rows & columns for each value.
    When a value has only one possible row/column remaining,
    it gets deleted from the candidate lists of cells in other
    boxes in the same row/column, and the row/column index for that
    value can be deleted (since it's served its purpose).

Indexes (Idea)

    Each cell or constraint group has a list of listeners,
    which need to be notified when a cell value is set, or
    it's candidates are changed.
