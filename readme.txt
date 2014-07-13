Constraint Group

    My own generic term for a row, column or box.  The 9 cells in a constraint
    group are "tied together" and constrained in that they collectively must
    contain each of the numbers 1 to 9 without repeats.

    When a cell value is set, the value can be removed from the candidates sets
    of all cells which are in the cell's same constraint groups.

Sudoku Solving Techniques

I will use the same names and techniques found here:

http://www.sudokuoftheday.com/techniques

Single Position

    When there's only one possible position (cell) in a constraint group that
    can contain a value.

    TODO: Finding these in a constraint group requires creating an index of
    sets of cell positions for each candidate value.

Single Candidate

    When there is only one possible candidate remaining for a particular cell.

Candidate Lines (TODO)

    When the only candidates for a particular value in a box lie on a line,
    therefore the same value candidates on same line in other boxes can be
    eliminated.

    These could be found by creating an index for each box which lists the
    possible rows & columns for each value in that box.  When a value has only
    one possible row/column remaining, it gets deleted from the candidate lists
    of cells in other boxes in the same row/column, and the row/column index
    for that value can be deleted (since it's served its purpose).

Listeners (Idea)

    Each cell or constraint group has a list of listeners,
    which need to be notified when a cell value is set, or
    it's candidates are changed.

Indexes (Idea)

    Indexes are like constraint groups in that they store data about
    candidates, with a view to detecting certain types of conditions for
    different solving techniques.

    For example, to detect Single Position, we could create an index on a
    constraint group which, for each value not yet found, lists which cells the
    value could occur in. Then, as soon as the length of the list of cells for
    any value is reduced to 1, the position of the value is known.

    Therefore the index would need to be notified whenever a cell value or its
    candidates change.

