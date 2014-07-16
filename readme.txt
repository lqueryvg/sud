Objectives
==========

- Learning Python OO and TDD

- Write a program which uses the same kinds of techniques that a human might
  use when solving Soduko puzzles, starting with the simplest techniques first
  and only applying the more complex techniques if the ones don't work.

- Make the puzzle solver code easy to extend when adding new solving
  techniques.  I.e. adding a new solving technique should not require changing
  code for existing techniques.

Terminology
-----------

Cells, Rows, Columns, Boxs

    Each individual puzzle cell contains a value from 1 to 9.
    Cells are arranged in a grid of 9 rows and 9 columns.
    The grid is divided into nine non-overlapping 3x3 boxes.

Candidates

    This is the set of possible values for a Cell when the actual cell value is
    not yet known. When the puzzle is empty, the candidate set for every cell
    contains the numbers 1 to 9.

Constraint Group

    A row, column or box.  The 9 cells in a constraint group are constrained
    together because they must contain numbers 1 to 9 without repeats.

    Every cell is a member of more than one constraint group; more specifically
    every cell is a member of 3 constraint groups: a row, a column and a box.

    When a cell value is known, the value can be removed from the candidates of
    all other cells in the cell's constraint groups.

Listeners

    Each cell has a list of listeners which want to be
    notified when the cell value is set or it's candidates change.

    (Might a constraint group also have listeners?)

Indexes (Idea)

    Indexes are like constraint groups in that they store data about
    candidates, with a view to detecting certain types of conditions for
    different solving techniques.

    For example, to detect Single Position, we could create an index on a
    constraint group which, for each value not yet found, lists which of the
    constraint group's cells the value could occur in. Then, as soon as the
    length of any of those lists is reduced to 1, there can only be one
    cell which can contain that value, so the position of the value it known.

    Therefore the index would need to be notified whenever a cell value or its
    candidates change.


Solving Techniques
------------------

Rather than re-invent the wheel, I'll use the same names for
the various solving techniques as can be found here:

http://www.sudokuoftheday.com/techniques

Simple Techniques
=================

Single Position

    When only one cell in a constraint group can contain a particular value.
    I.e. the value has been eliminated from the candidates of all other
    cells in the constraint group.

    TODO: Finding these in a constraint group requires creating an index of
    sets of cell positions for each candidate value.

Single Candidate

    When there is only one possible candidate remaining for a particular cell.

Medium Techniques
=================

Candidate Lines (TODO)

    When the only candidates for a particular value in a box lie on a line,
    therefore the same value candidates on same line in other boxes can be
    eliminated.

    These could be found by creating an index for each box which lists the
    possible rows & columns for each value in that box.  When a value has only
    one possible row/column remaining, it gets deleted from the candidate lists
    of cells in other boxes in the same row/column, and the row/column index
    for that value can be deleted (since it's served its purpose).

