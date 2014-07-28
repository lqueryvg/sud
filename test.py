#!/usr/bin/env python2

from sud2 import *
import unittest

def init_logging():
    import logging

    hdlr = logging.StreamHandler()
    hdlr.setFormatter(
        logging.Formatter("%(levelname)s %(message)s")
    )
    logging.getLogger().addHandler(hdlr)

init_logging()


class TestCandidateSet(unittest.TestCase):
    def suppress_test_constructor_zero_elements(self):
        self.assertRaisesRegexp(AssertionError,
                'At least two candidates required',
                          CandidateSet, [])

    def suppress_test_constructor_one_element(self):
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
        #import pdb; pdb.set_trace()
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
        obj.candidates.remove_candidate(2)
        self.assertFalse(2 in obj.candidates)
        self.assertTrue(1 in obj.candidates)
        self.assertTrue(3 in obj.candidates)


class TestConstraintGroup(unittest.TestCase):
    def setUp(self):
        #logging.getLogger().setLevel(logging.DEBUG)
        pass

    def test_notify(self):
        #import pdb; pdb.set_trace()
        cell00 = Cell([1, 2], row=0, col=0)
        cell01 = Cell([1, 2], row=0, col=1)
        grp = ConstraintGroup([cell00, cell01])
        cell00.set_value(1)
        self.assertTrue(cell01.get_value() == 2)

    def tearDown(self):
        #logging.getLogger().setLevel(logging.CRITICAL)
        pass


class TestGrid(unittest.TestCase):
    def test_grid_rc(self):
        grid = Grid(2)
        grid.set_grid_rc_value(0, 0, 1)
        grid.set_grid_rc_value(0, 1, 2)
        grid.set_grid_rc_value(1, 0, 3)
        grid.set_grid_rc_value(1, 1, 4)
        self.assertTrue(grid.get_cell(0, 0) == 1)
        self.assertTrue(grid.get_cell(0, 1) == 2)
        self.assertTrue(grid.get_cell(1, 0) == 3)
        self.assertTrue(grid.get_cell(1, 1) == 4)

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
        puzzle = Puzzle(2)


class TestLoadAndParse(unittest.TestCase):
    def test_load_errors(self):
        puzzle = Puzzle(2)
        self.assertRaisesRegexp(PuzzleParseError,
                'unexpected number of words',
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
                    .. ..
                    .. ..

                    .. ..
                    .. ..

                    .. ..
                """)

    def test_load_candidates_unexpected_number_of_words(self):
        puzzle = Puzzle(2)
        self.assertRaisesRegexp(PuzzleParseError,
                'unexpected number of words',
                puzzle.load_candidates_from_string, ('wibble')
                )

    def test_load_candidates_too_many_rows(self):
        puzzle = Puzzle(2)
        self.assertRaisesRegexp(PuzzleParseError,
                'too many rows',
                puzzle.load_candidates_from_string,
                """
                    . . . .
                    . . . .

                    . . . .
                    . . . .

                    . . . .
                """)

    def test_load_candidates_some_values(self):
        puzzle = Puzzle(2)
        logging.getLogger().setLevel(logging.INFO)
        try:
            puzzle.init_all_candidates()
            logging.info("Before loading candidates:\n" + puzzle.to_string())
            #import pdb; pdb.set_trace()
            puzzle.load_candidates_from_string(
                """
                    12 1 . .
                    . . . .

                    . . . .
                    . . . .

                """)
            logging.info("After loading candidates:\n" + puzzle.to_string())

        finally:
            # turn off info/debug
            logging.getLogger().setLevel(logging.CRITICAL)


class TestSolvers(unittest.TestCase):
    def test_puzzle_create(self):
        puzzle = Puzzle(2)

    def test_single_candidate(self):
        puzzle = Puzzle(2)
        puzzle.init_all_candidates();
        puzzle.load_from_string(
            """
            12 3.
            .. ..

            .. ..
            .. ..
            """
            )
        self.assertTrue(puzzle.get_cell(0, 3).value == 4)
        self.assertTrue(1 not in puzzle.get_cell(0, 3).candidates)
        #print "\n" + puzzle.to_string()
        #import pdb; pdb.set_trace()
        #puzzle.get_cell(2, 2).set_value(1)
        #print str.join("\n", puzzle.solution_steps)
        #print puzzle.to_string()

    def test_single_position(self):
        puzzle = Puzzle(2)
        puzzle.init_all_candidates();
        puzzle.load_from_string(
            """
            1. ..
            .. ..

            .. 1.
            .. ..
            """
            )
        #print "\n" + puzzle.to_string()
        #import pdb; pdb.set_trace()
        self.assertTrue(puzzle.get_cell(1, 3).value is None)
        self.assertTrue(puzzle.get_cell(3, 1).value is None)

        puzzle.add_SinglePosition()

        self.assertTrue(puzzle.get_cell(1, 3).value == 1)
        self.assertTrue(puzzle.get_cell(3, 1).value == 1)
        #print "\n" + puzzle.to_string()
        #print str.join("\n", puzzle.solution_steps)

    def test_candidate_lines1(self):
        puzzle = Puzzle(3)
        puzzle.init_all_candidates();
        puzzle.load_from_string(
            """
            123 ... ...
            456 ... ...
            ... ... ...

            ... ... ...
            ... ... ...
            ... ... ...

            ... ... ...
            ... ... ...
            ... ... ...
            """
            )
        self.assertTrue(7 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(8 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(9 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(7 in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(8 in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(9 in puzzle.get_cell(2, 6).candidates)
        #logging.getLogger().setLevel(logging.INFO)
        logging.info("Before puzzle.add_CandidateLines:\n" + puzzle.to_string())
        puzzle.add_CandidateLines()
        logging.info("After puzzle.add_CandidateLines:\n" + puzzle.to_string())
        #import pdb; pdb.set_trace()
        #logging.getLogger().setLevel(logging.CRITICAL)
        self.assertTrue(7 in puzzle.get_cell(2, 0).candidates)
        self.assertTrue(7 in puzzle.get_cell(2, 1).candidates)
        self.assertTrue(7 in puzzle.get_cell(2, 2).candidates)
        self.assertTrue(7 in puzzle.get_cell(0, 3).candidates)
        self.assertTrue(7 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(8 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(9 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(7 not in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(8 not in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(9 not in puzzle.get_cell(2, 6).candidates)

    def test_candidate_lines2(self):
        puzzle = Puzzle(3)
        #import pdb; pdb.set_trace()
        puzzle.init_all_candidates();
        puzzle.add_CandidateLines()
        self.assertTrue(7 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(8 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(9 in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(7 in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(8 in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(9 in puzzle.get_cell(2, 6).candidates)
        #logging.getLogger().setLevel(logging.INFO)
        logging.info("Before set_value(0,0,1):\n" + puzzle.to_string())
        puzzle.get_cell(0, 0).set_value(1)
        logging.info("After set_value(0,0,1):\n" + puzzle.to_string())
        puzzle.get_cell(0, 1).set_value(2)
        logging.info("After set_value(0,1,2):\n" + puzzle.to_string())
        puzzle.get_cell(0, 2).set_value(3)
        puzzle.get_cell(1, 0).set_value(4)
        puzzle.get_cell(1, 1).set_value(5)
        logging.info("After set_value(1,1,5):\n" + puzzle.to_string())
        puzzle.get_cell(1, 2).set_value(6)
        logging.info("After set_value calls:\n" + puzzle.to_string())
        logging.getLogger().setLevel(logging.CRITICAL)
        #print str.join("\n", puzzle.solution_steps)
        self.assertTrue(7 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(8 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(9 not in puzzle.get_cell(2, 3).candidates)
        self.assertTrue(7 not in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(8 not in puzzle.get_cell(2, 6).candidates)
        self.assertTrue(9 not in puzzle.get_cell(2, 6).candidates)

if __name__ == '__main__':
    unittest.main(verbosity=2)
