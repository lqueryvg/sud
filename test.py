#!/usr/bin/env python2

# import sud2
from sud2 import *
import unittest


class TestCandidateSet(unittest.TestCase):
    def test_constructor_zero_elements(self):
        self.assertRaises(AtLeastTwoCandidateValuesRequired,
                          CandidateSet, [])

    def test_constructor_one_element(self):
        self.assertRaises(AtLeastTwoCandidateValuesRequired,
                          CandidateSet, ["one"])

    def test_remove_candidate(self):
        obj = CandidateSet([1, 3, 2])
        obj.remove_candidate(2)
        self.assertFalse(2 in obj)
        self.assertTrue(1 in obj)
        self.assertTrue(3 in obj)

    def test_remove_final_candidate(self):
        obj = CandidateSet([1, 2])
        try:
            obj.remove_candidate(1)
        except:
            pass
        self.assertRaises(AssertionError, obj.remove_candidate, 2)

    def test_remove_SingleCandidate(self):
        obj = CandidateSet([1, 2])
        self.assertRaises(SingleCandidate, obj.remove_candidate, 2)

    def test_remove_ValueError_on_remove_element_not_there(self):
        obj = CandidateSet([1, 2])
        self.assertRaises(KeyError, obj.remove_candidate, 3)


class TestCell(unittest.TestCase):
    def test_set_then_get(self):
        cell = Cell([1, 2, 3])
        cell.set_value(1)
        self.assertTrue(cell.get_value() == 1)

#    def test_set_value_already_set(self):
#        cell = Cell([1, 2, 3])
#        cell.set_value(1)
#        self.assertRaises(CellAlreadySet, cell.set_value, 1)

    def test_set_value_not_a_candidate(self):
        cell = Cell([1, 2])
        self.assertRaises(ValueIsNotACandidate, cell.set_value, 3)

    def test_remove_candidate(self):
        # Check inheritance works
        obj = Cell([1, 3, 2])
        obj.remove_candidate(2)
        self.assertFalse(2 in obj)
        self.assertTrue(1 in obj)
        self.assertTrue(3 in obj)


class TestConstraintGroup(unittest.TestCase):
    def test_notify(self):
        cell1 = Cell([1, 2])
        cell2 = Cell([1, 2])
        grp = ConstraintGroup([cell1, cell2])
        cell1.set_value(1)
        self.assertTrue(cell2.get_value() == 2)


class TestGrid(unittest.TestCase):
    def test_grid_rc(self):
        grid = Grid(2)
        grid.set_grid_rc_value(0, 0, 1)
        grid.set_grid_rc_value(0, 1, 2)
        grid.set_grid_rc_value(1, 0, 3)
        grid.set_grid_rc_value(1, 1, 4)
        self.assertTrue(grid.get_grid_rc_value(0, 0) == 1)
        self.assertTrue(grid.get_grid_rc_value(0, 1) == 2)
        self.assertTrue(grid.get_grid_rc_value(1, 0) == 3)
        self.assertTrue(grid.get_grid_rc_value(1, 1) == 4)

    def test_get_box(self):
        grid = Grid(2)
        grid.set_grid_rc_value(0, 0, 1)
        grid.set_grid_rc_value(0, 1, 2)
        grid.set_grid_rc_value(1, 0, 3)
        grid.set_grid_rc_value(1, 1, 4)
        box = grid.get_box(0, 0)
        self.assertTrue(len(box) == 4)


class TestPuzzle(unittest.TestCase):
    def test_puzzle_create(self):
        puzzle = Puzzle(2);

    def test_puzzle_parse_error(self):
        puzzle = Puzzle(2);
        self.assertRaisesRegexp(PuzzleParseError,
                'expect \w* words \(one per box\)',
                puzzle.load_from_string, ('wibble')
                )
        self.assertRaisesRegexp(PuzzleParseError,
                'length of word .* must match box width',
                puzzle.load_from_string, ('a b')
                )
        self.assertRaisesRegexp(PuzzleParseError,
                'too many rows',
                puzzle.load_from_string,
                """
                    -- --
                    -- --

                    -- --
                    -- --

                    -- --
                """)

    def test_simple_puzzle(self):
        puzzle = Puzzle(2);
        puzzle.load_from_string(
            """
            12 3-
            34 --

            -- --
            -- --
            """
            )
        #import pdb; pdb.set_trace()
        self.assertTrue(puzzle.get_grid_rc_value(0, 3).value == 4)
        #print str.join("\n", puzzle.log)

if __name__ == '__main__':
    unittest.main(verbosity=2)
