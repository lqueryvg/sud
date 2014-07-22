Objectives
==========

- Learning Python OO and TDD

- Use the same strategies a human might when solving Soduko, starting with
  the simplest and only applying the more complex strategies
  when needed.

- Make the solver code easy to extend when adding new strategies.  I.e.
  adding a new strategy should not require changing code for existing
  strategies.

Terminology
-----------

Cells, Rows, Columns, Boxes

    Each puzzle cell contains a value from 1 to 9.
    Cells are arranged in a grid of 9 rows and 9 columns.
    The grid is divided into nine non-overlapping 3x3 boxes.
    
    Note: Different sized grids (4x4, 9x9, 16x16, etc) are only partially
    supported; specifically the cells values when reading from a string
    or file must be 1 character, but internally the values in each
    cell are expected to be 1 up to the box width squared.
    This obviously wouldn't work for 16x16 grids.

Candidates

    The set of possible values for a cell when the cell value is
    not yet known. When the puzzle is empty, the candidates for every cell
    will be the set of numbers from 1 to 9 inclusive.

Constraint Group

    A grouping of 9 cells in a row, column or box.  The cells in any constraint
    group must contain the numbers 1 to 9 without repeats.

    Every cell can be a member of more than one constraint group; in fact
    every cell is a member of 3 constraint groups: a row, a column
    and a box.

    When a cell value is known, the value can be removed from the candidates of
    all other cells in the cell's 3 constraint groups.

Listeners

    When a cell is changed the cell can notify other objects of the change.
    Objects register themselves with cells to say that they are interested.
    
    Each cell has 2 lists of listeners waiting for notifications.
    Each list is for listeners interested in a specific type of
    cell change. The 2 types are:
    
    1. Cell candidate removed.

        The SingleCandidate class (and others) will need to listen for this.
        If a cell's the penultimate candidate is removed, SingleCandidate will
        need to set the cell's value to the only remaining candidate.

    2. Cell value set.

        A ConstraintGroup will need to listen for cell values being set so it
        can remove the value from the candidates of all other cells in the
        group.

        Once a cell value has been set, the value set listeners are first
        notified then all listeners and the candidates list are removed
        (cleared) from the cell (since there can be no further changes to this
        cell).

        Note that candidate removed listeners are *not* called when the
        candidate list is cleared in this situation, because (for example) if
        there are 4 candidates and 5 candidate remove listeners, we would have
        to call each listener once for each candidate being removed, i.e. 4 x 5
        = 20 calls.  It is therefore expected that a class interested in cell
        candidates removals also listens for cell values being set.

Indexes (Idea)

    Indexes are like constraint groups in that they store data about
    candidates, with a view to detecting conditions for different solving
    strategies.

    For example, to detect Single Position, we could create an index on a
    constraint group which, for each value not yet found, lists the cells the
    value could occur in. Then, as soon as the length of any of those lists is
    reduced to 1, there can only be one cell which can contain that value, so
    the position of the value becomes known.

    Therefore the index would need to be notified whenever a cell value is
    set or a cell candidate is removed.

    (Perhaps an Index *is* a more general form of a constraint group?  I.e.
    perhaps a constraint group should be generalised into a single candidate
    index?)


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

Single Candidate

    When there is only one possible candidate remaining for a particular cell.

Medium Techniques
=================

Candidate Lines (TODO)

    The only candidates for a value in a box lie on a line (i.e. row or
    column), so the same value in other boxes on the same line can be
    eliminated.

    Creating an index for each box listing the
    possible rows & columns for each value in that box.

    rows{value} -> [ rownum1, rownum2, ...]
    cols{value} -> [ colnum1, colnum2, ...]
    
    When a value has only
    one possible row/column remaining, it gets deleted from the candidate lists
    of cells in other boxes in the same row/column, and the row/column index
    for that value can be deleted (since it's served its purpose).

