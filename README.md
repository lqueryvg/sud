# Sud

## Objectives

- Learning Python OO and TDD

- Use the same strategies a human might when solving Soduko, starting with
  the simplest and only applying the more complex strategies
  when needed.

  Rather than re-invent the wheel, I'll use the same names for the various
  solving techniques as found here:

  http://www.sudokuoftheday.com/techniques

- Make the solver code easy to extend when adding new strategies.  I.e.
  adding a new strategy should not require changing code for existing
  strategies.

## Terminology

### Cells, Rows, Columns, Boxes

Each puzzle cell contains a value from 1 to 9.  Cells are arranged in a grid of
9 rows and 9 columns.  The grid is divided into nine non-overlapping 3x3 boxes.
    
Note: Different sized grids (4x4, 9x9, 16x16, etc) are only partially
supported; specifically the cell values when reading from a string or file
must be 1 character, but internally the values in each cell are expected to be
1 up to the box width squared.  This obviously wouldn't work for 16x16 grids.

### Candidates

The set of possible values for a cell when the cell value is not yet known.
When the puzzle is empty, the candidates for every cell will be the set of
numbers from 1 to 9 inclusive.

### CellGroup

A grouping of 9 cells in a row, column or box.  The Cell Group is given a name,
eg. 'Row0', 'Col3' or 'Box03'.  For boxes, the name includes the row and col
number of the top-left cell in the box.

Every cell is a member of exactly 3 cell groups: a row, a column and a box.

### UniqueConstraint

UniqueConstraint ensures there are no repeated values within a cell
group.

When a cell value becomes known, the value is removed from the
candidates of all other cells in the cell's 3 constraint groups.

### Listeners

When a cell is changed the cell can notify other objects.  Objects must
register themselves with cells to say they are interested.
    
Each cell has 2 lists of listeners waiting for notifications, one list
for each of the following types of event:

1. **CandidateRemoved**

 The SingleCandidate class (and others) will need to listen for this.
 If a cell's penultimate candidate is removed, SingleCandidate will
 need to set the cell's value to the only remaining candidate.

2. **ValueSet**

 Once a cell value has been set, the ValueSet listeners are first
 notified. Then all listeners and candidates are removed from the
 cell.

 NOTE CandidateRemoved listeners are *NOT* notified when the
 candidate list is cleared in this situation, since it would generate a
 lot of unecessary calls.  For example, if there are 4 candidates and 5
 listeners, there would be 4 x 5 = 20 calls.
        
 Therefore an object interested in CandidateRemoved events should also
 listen for ValueSet events.

 Conversly, it is conceivable that an object interested in 
 ValueSet events might *NOT* care about CandidateRemoved events.


## Solving Techniques

### Simple Techniques

#### Single Position

When only one cell in a constraint group can contain a particular value.
I.e. the value has been eliminated from the candidates of all other
cells in the constraint group.

#### Single Candidate

When there is only one possible candidate remaining for a particular cell.

### Medium Techniques

#### Candidate Lines

If the only candidates for a value in a box lie on a line (i.e.
a row or column) within the box, eliminates the value from
candidates of cells in other boxes on the same line.

This is done by maintaining an index as follows:

> For every value not yet known in the box, index the list of rows and
> cols the value can be on.  For each of those rows/cols, store the list
> of cells within the box the value can be in.

When a value has only one possible row/column remaining, it gets deleted
from the candidate lists of cells in other boxes in the same row/column,
and the row/column index for the value can be deleted (since it's served
its purpose).
