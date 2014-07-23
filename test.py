#!/usr/bin/env python2

# import sud2
from sud2 import *
import unittest


class TestCandidateSet(unittest.TestCase):
    def test_constructor_zero_elements(self):
        self.assertRaisesRegexp(AssertionError,
                'At least two candidates required',
                          CandidateSet, [])

    def test_constructor_one_element(self):
        self.assertRaisesRegexp(AssertionError,
                'At least two candidates required',
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

    def test_set_value_not_a_candidate(self):
        cell = Cell([1, 2])
        self.assertRaisesRegexp(AssertionError,
                'Value is not a candidate',
                          cell.set_value, 3)

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
        self.assertTrue(grid.get_grid_cell(0, 0) == 1)
        self.assertTrue(grid.get_grid_cell(0, 1) == 2)
        self.assertTrue(grid.get_grid_cell(1, 0) == 3)
        self.assertTrue(grid.get_grid_cell(1, 1) == 4)

    def test_get_box_cells(self):
        grid = Grid(2)
        grid.set_grid_rc_value(0, 0, 1)
        grid.set_grid_rc_value(0, 1, 2)
        grid.set_grid_rc_value(1, 0, 3)
        grid.set_grid_rc_value(1, 1, 4)
        box = grid.get_box_cells(0, 0)
        self.assertTrue(len(box) == 4)


class TestPuzzle(unittest.TestCase):
    def test_puzzle_create(self):
        puzzle = Puzzle(2);

    def test_puzzle_parse_errors(self):
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

    def test_single_candidate(self):
        puzzle = Puzzle(2);
        puzzle.load_from_string(
            """
            12 3-
            -- --

            -- --
            -- --
            """
            )
        self.assertTrue(puzzle.get_grid_cell(0, 3).value == 4)
        #print puzzle.to_string()
        #import pdb; pdb.set_trace()
        #puzzle.get_grid_cell(2, 2).set_value(1)
        #print str.join("\n", puzzle.solution)
        #print puzzle.to_string()

    def test_single_position(self):
        puzzle = Puzzle(2);
        puzzle.load_from_string(
            """
            1- --
            -- --

            -- 1-
            -- --
            """
            )
        #print "\n" + puzzle.to_string()
        #import pdb; pdb.set_trace()
        self.assertTrue(puzzle.get_grid_cell(1, 3).value is None)
        self.assertTrue(puzzle.get_grid_cell(3, 1).value is None)

        puzzle.add_SinglePosition()

        self.assertTrue(puzzle.get_grid_cell(1, 3).value == 1)
        self.assertTrue(puzzle.get_grid_cell(3, 1).value == 1)
        #print "\n" + puzzle.to_string()
        #print str.join("\n", puzzle.solution)

    def test_candidate_lines1(self):
        puzzle = Puzzle(3);
        puzzle.load_from_string(
            """
            123 --- ---
            456 --- ---
            --- --- ---

            --- --- ---
            --- --- ---
            --- --- ---

            --- --- ---
            --- --- ---
            --- --- ---
            """
            )
        print "\n" + puzzle.to_string()
        self.assertTrue(7 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(8 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(9 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(7 in puzzle.get_grid_cell(2, 6))
        self.assertTrue(8 in puzzle.get_grid_cell(2, 6))
        self.assertTrue(9 in puzzle.get_grid_cell(2, 6))
        puzzle.add_CandidateLines()
        self.assertTrue(7 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(8 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(9 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(7 not in puzzle.get_grid_cell(2, 6))
        self.assertTrue(8 not in puzzle.get_grid_cell(2, 6))
        self.assertTrue(9 not in puzzle.get_grid_cell(2, 6))

    def test_candidate_lines2(self):
        puzzle = Puzzle(3);
        puzzle.add_CandidateLines()
        self.assertTrue(7 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(8 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(9 in puzzle.get_grid_cell(2, 3))
        self.assertTrue(7 in puzzle.get_grid_cell(2, 6))
        self.assertTrue(8 in puzzle.get_grid_cell(2, 6))
        self.assertTrue(9 in puzzle.get_grid_cell(2, 6))
        #import pdb; pdb.set_trace()
        puzzle.get_grid_cell(0, 0).set_value(1)
        puzzle.get_grid_cell(0, 1).set_value(2)
        puzzle.get_grid_cell(0, 2).set_value(3)
        puzzle.get_grid_cell(1, 0).set_value(4)
        puzzle.get_grid_cell(1, 1).set_value(5)
        puzzle.get_grid_cell(1, 2).set_value(6)
        self.assertTrue(7 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(8 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(9 not in puzzle.get_grid_cell(2, 3))
        self.assertTrue(7 not in puzzle.get_grid_cell(2, 6))
        self.assertTrue(8 not in puzzle.get_grid_cell(2, 6))
        self.assertTrue(9 not in puzzle.get_grid_cell(2, 6))

if __name__ == '__main__':
    unittest.main(verbosity=2)
