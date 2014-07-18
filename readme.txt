Objectives
==========

- Learning Python OO and TDD

- Use the same techniques a human might use when solving Soduko, starting with
  the simplest techniques first and only applying the more complex techniques
  if needed.

- Make the solver code easy to extend when adding new solving techniques.  I.e.
  adding a new solving technique should not require changing code for existing
  techniques.

Terminology
-----------

Cells, Rows, Columns, Boxes

    Each puzzle cell contains a value from 1 to 9.
    Cells are arranged in a grid of 9 rows and 9 columns.
    The grid is divided into nine non-overlapping 3x3 boxes.
    Maybe add support for different sized grids (4x4, 9x9, 16x16, etc).

Candidates

    The set of possible values for a Cell when the actual cell value is
    not yet known. When the puzzle is empty, the candidate set for every cell
    will be the set of numbers from 1 to 9 inclusive.

Constraint Group

    A grouping of 9 cells in a row, column or box.  The cells in any constraint
    must contain numbers 1 to 9 without repeats.

    Every cell can be a member of more than one constraint group; more
    specifically every cell is a member of 3 constraint groups: a row, a column
    and a box.

    When a cell value is known, the value can be removed from the candidates of
    all other cells in the cell's 3 associated constraint groups.

Listeners

    Each cell has the ability to 2 lists of listeners waiting for notifications.
    There are 2 types of notification. Each list is for 
    Each list is for listeners 
    , one list for
    each type of n
    
    1. Cell candidate removed.

        The SingleCandidate class (and others) will need to listen for this.
        If a cell's the penultimate candidate is removed, SingleCandidate will
        need to set the cell's value to the only remaining candidate.

    2. Cell value set.

        A ConstraintGroup will need to listen for cell values being set so it
        can remove the value from the candidates of all other cells in the
        group.

        Once a cell value is set, the value set listeners are first notified
        then both listener lists and the candidate lists are cleared (since
        there cen be no further changes to this cell).

        Note that candidate removed listeners are *not* called when the
        candidate list is cleared in this situation, because (for example) if
        there are 4 candidates and 5 candidate remove listeners, we would have
        to call each listener once for each candidate being removed, i.e. 4 x 5
        = 20 calls.  It is therefore expected that a class interested in cell
        candidates removals also listens for cell values being set.

Indexes (Idea)

    Indexes are like constraint groups in that they store data about
    candidates, with a view to detecting certain types of conditions for
    different solving techniques.

    For example, to detect Single Position, we could create an index on a
    constraint group which, for each value not yet found, lists the cells the
    value could occur in. Then, as soon as the length of any of those lists is
    reduced to 1, there can only be one cell which can contain that value, so
    the position of the value becomes known.

    Therefore the index would need to be notified whenever a cell value or its
    candidates change.

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

    TODO: Finding these in a constraint group requires creating an index of
    sets of cell positions for each candidate value.

Single Candidate

    When there is only one possible candidate remaining for a particular cell.

Medium Techniques
=================

Candidate Lines (TODO)

    When the only candidates for a value in a box lie on a line,
    therefore the same value in other boxes on the same line can be
    eliminated.

    These could be found by creating an index for each box which lists the
    possible rows & columns for each value in that box.  When a value has only
    one possible row/column remaining, it gets deleted from the candidate lists
    of cells in other boxes in the same row/column, and the row/column index
    for that value can be deleted (since it's served its purpose).

Random Thoughts
---------------
(Chronological Order)

    Would be nice to have more control over when the solving takes
    place. At the moment it happens recursively, so just setting
    a cell could cause solving to occur.

    Perhaps setting a cell values should not also trigger candidate
    removal in constraint groups, and everything should be done
    via listeners.

    So, SingleCandidate can be an object associated with every
    cell (which doesn't have a value set) which listens for candidate
    removals. When the last candidate has been removed, it sets the cells
    value.
