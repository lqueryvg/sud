#!/usr/bin/env python2

from sud2 import *
import unittest
from textwrap import dedent

def init_logging():
    import logging

    hdlr = logging.StreamHandler()
    hdlr.setFormatter(
        logging.Formatter("%(levelname)s %(message)s")
    )
    logging.getLogger().addHandler(hdlr)


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
        obj.candidate_set.remove_candidate(2)
        self.assertFalse(2 in obj.candidate_set)
        self.assertTrue(1 in obj.candidate_set)
        self.assertTrue(3 in obj.candidate_set)


class TestUniqueConstraints(unittest.TestCase):
    def setUp(self):
        #logging.getLogger().setLevel(logging.DEBUG)
        pass

    def test_unique_constraint_finds_single_candidate(self):
        #import pdb; pdb.set_trace()
        cell00 = Cell([1, 2], row=0, col=0)
        cell01 = Cell([1, 2], row=0, col=1)
        dummy = UniqueConstraints(
                CellGroup([cell00, cell01])
        )
        cell00.set_value(1)
        self.assertTrue(cell01.get_value() == 2)

    def test_unique_constraint_violations(self):
        cell00 = Cell([1, 2, 3], row=0, col=0)
        cell01 = Cell([1, 2, 3], row=0, col=1)
        cell02 = Cell([1, 2, 3], row=0, col=2)
        cell00.set_value(1)
        cell01.set_value(1)
        cell02.set_value(1)
        #import pdb; pdb.set_trace()
        self.assertRaisesRegexp(
            Exception,
            'UniqueConstraints broken',
            UniqueConstraints,
            CellGroup([cell00, cell01, cell02])
        )
        # now check exception args are what we expect
        try:
            dummy = UniqueConstraints(CellGroup([cell00, cell01, cell02]))
        except Exception as e:
            self.assertTrue(e.args[1][0] == [1, cell01, cell00])
            self.assertTrue(e.args[1][1] == [1, cell02, cell00])

    def tearDown(self):
        logging.getLogger().setLevel(logging.CRITICAL)
        pass


class TestGrid(unittest.TestCase):
    def test_grid_rc(self):
        grid = Grid(2)
        for (r, c, v) in [
                            (0, 0, 1),
                            (0, 1, 2),
                            (1, 0, 3),
                            (1, 1, 4)
        ]:
            grid.set_value(r, c, v)
        grid.set_value(1, 1, 4)

        self.assertTrue(
            (
                grid.get_cell(0, 0),
                grid.get_cell(0, 1),
                grid.get_cell(1, 0),
                grid.get_cell(1, 1)
            ) == (1, 2, 3, 4)
        )

    def test_get_box_cells(self):
        grid = Grid(2)

        for (r, c, v) in [
                            (0, 0, 1),
                            (0, 1, 2),
                            (1, 0, 3),
                            (1, 1, 4)
        ]:
            grid.set_value(r, c, v)

        box = grid.get_box_cells(0, 0)
        self.assertTrue(len(box) == 4)
        self.assertTrue(sum(box) == 10)


class TestPuzzle(unittest.TestCase):
    def test_puzzle_create(self):
        dummy = Puzzle(2)


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
        puzzle1 = Puzzle(2)
        puzzle2 = Puzzle(2)
        #logging.getLogger().setLevel(logging.INFO)
        try:
            logging.info("puzzle1:\n" + puzzle1.to_string())
            logging.info("puzzle2:\n" + puzzle2.to_string())
            #import pdb; pdb.set_trace()
            puzzle1.load_candidates_from_string(
                """
                    1       34  1234  1234   
                    12    1234    3   1234   

                    1234  1234  1234  123    
                    1234    34  1234  1234   

                """)
            puzzle2.load_candidates_from_string(
                """
                    1       34     .     .   
                    12       .    3      .   

                       .     .     .  123    
                       .    34     .     .   
                """)
            logging.info("puzzle1:\n" + puzzle1.to_string())
            logging.info("puzzle2:\n" + puzzle2.to_string())
            self.assertTrue(puzzle1.is_equal_to(puzzle2))
            #logging.info("After loading candidates:\n" + puzzle.to_string())

        finally:
            # turn off info/debug
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_load_candidates_silly_values(self):
        #logging.getLogger().setLevel(logging.INFO)
        try:
            #import pdb; pdb.set_trace()
            puzzle = Puzzle(2)
            logging.info("puzzle:\n" + puzzle.to_string())
            #logging.info("After loading candidates:\n" + puzzle.to_string())
            self.assertRaisesRegexp(PuzzleParseError,
                    "invalid candidate\(s\) found in word",
                    puzzle.load_candidates_from_string,
                    """
                        1&&&   x34  1234  1234   
                        12    1234  --3-  1234   

                        1234  1234  1234  123    
                        1034   *34  1234  1234   
                    """)

        finally:
            # turn off info/debug
            logging.getLogger().setLevel(logging.CRITICAL)


class TestSolvers(unittest.TestCase):

    def test_single_candidate(self):
        #logging.getLogger().setLevel(logging.INFO)
        puzzle = Puzzle(2)

        try:
            UniqueConstraints.add_to_puzzle(puzzle)
            puzzle.load_from_string(
                """
                12 3.
                .. ..

                .. ..
                .. ..
                """
                )
            expected = Puzzle(2)
            expected.load_candidates_from_string(
                """
                    1         2     |    3         4     
                    34        34    |    12        12    
                #-------------------+--------------------
                   234       134    |   124       123    
                   234       134    |   124       123    
                """
                )
            self.assertTrue(puzzle.is_equal_to(expected))
        finally:
            logging.info("test_single_candidate() puzzle =\n" + puzzle.to_string())
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_single_position(self):
        puzzle = Puzzle(2)
        #logging.getLogger().setLevel(logging.INFO)

        try:
            #import pdb; pdb.set_trace()
            UniqueConstraints.add_to_puzzle(puzzle)
            puzzle.load_from_string(
                """
                1. ..
                .. ..

                .. 1.
                .. ..
                """
                )
            #print "\n" + puzzle.to_string()
            self.assertTrue(puzzle.get_cell(1, 3).value is None)
            self.assertTrue(puzzle.get_cell(3, 1).value is None)
            logging.info("test_single_position() before adding SinglePosition,"
                    " puzzle =\n" + puzzle.to_string())
            logging.info("create/load expected puzzle")

            #puzzle.add_SinglePosition()
            SinglePosition.add_to_puzzle(puzzle)
            logging.info("puzzle after adding SinglePosition = \n"
                    + puzzle.to_string())

            expected = Puzzle(2)
            expected.load_candidates_from_string(
                """
                    1        234    |   234       234
                   234       234    |   234       1
                #-------------------+--------------------
                   234       234    |    1        234
                   234       1      |   234       234
                """
                )
            logging.info("expected puzzle = \n" + expected.to_string())

            self.assertTrue(puzzle.is_equal_to(expected))

            #import pdb; pdb.set_trace()
            self.assertTrue(puzzle.get_cell(1, 3).value == '1')
            self.assertTrue(puzzle.get_cell(3, 1).value == '1')
            logging.info("test_single_position() puzzle =\n" +
                    puzzle.to_string())
        finally:
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_candidate_lines0(self):
        puzzle = Puzzle(2)
        #logging.getLogger().setLevel(logging.INFO)
        try:
            puzzle.load_candidates_from_string(
                """
                    1      2    1234  1234   
                      34    34  1234  1234   

                    1234  1234  1234  1234   
                    1234  1234  1234  1234   
                """
                )
            logging.info("before adding CandidateLines puzzle = \n"
                    + puzzle.to_string())
            #puzzle.add_CandidateLines()
            CandidateLines.add_to_puzzle(puzzle)
            logging.info("After adding CandidateLines puzzle = \n"
                    + puzzle.to_string())
            expected = Puzzle(2)
            expected.load_candidates_from_string(
                """
                    1      2    1234  1234   
                      34    34  12    12     

                    1234  1234  1234  1234   
                    1234  1234  1234  1234   
                """
                )
            self.assertTrue(puzzle.is_equal_to(expected))
        finally:
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_candidate_lines01(self):
        puzzle = Puzzle(2)
        #logging.getLogger().setLevel(logging.INFO)
        try:
            puzzle.load_candidates_from_string(
                """
                    1234  1234    34    34   
                    1234  1234  1234  1234   

                    1234  1234  1234  1234   
                    1234  1234  1234  1234   
                """
                )
            logging.info("before adding CandidateLines puzzle = \n"
                    + puzzle.to_string())
            #puzzle.add_CandidateLines()
            CandidateLines.add_to_puzzle(puzzle)
            logging.info("After adding CandidateLines puzzle = \n"
                    + puzzle.to_string())
            expected = Puzzle(2)
#            expected.load_candidates_from_string(
#                """
#                    1234  1234    34    34   
#                      34    34  1234  1234   
#
#                    1234  1234  1234  1234   
#                    1234  1234  1234  1234   
#                """
            expected.load_candidates_from_string2(dedent(
                """\
                    12 12 |      
                    34 34 | 34 34

                          | 12 12
                    34 34 | 34 34
                    #-----+------
                    12 12 | 12 12
                    34 34 | 34 34

                    12 12 | 12 12
                    34 34 | 34 34
                """
                ))
            logging.info("Expected = \n"
                    + expected.to_string())
            self.assertTrue(puzzle.is_equal_to(expected))
        finally:
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_candidate_lines1(self):
        puzzle = Puzzle(3)
        #logging.getLogger().setLevel(logging.INFO)

        try:
            # TODO test this in isolation without UniqueConstraints
            UniqueConstraints.add_to_puzzle(puzzle)
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

            logging.info("Before puzzle.add_CandidateLines:\n" + puzzle.to_string())

            expected = Puzzle(3)
            expected.load_candidates_from_string2(dedent(
#                """
#                    1         2         3    |  456789    456789    456789  |  456789    456789    456789
#                    4         5         6    |  123789    123789    123789  |  123789    123789    123789
#                   789       789       789   |123456789 123456789 123456789 |123456789 123456789 123456789
#                #----------------------------+------------------------------+------------------------------
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                #----------------------------+------------------------------+------------------------------
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                2356789   1346789   1245789  |123456789 123456789 123456789 |123456789 123456789 123456789
#                """
            """\
               1    2    3 |             |            
                           | 456 456 456 | 456 456 456
                           | 789 789 789 | 789 789 789

                           | 123 123 123 | 123 123 123
               4    5    6 |             |            
                           | 789 789 789 | 789 789 789

                           | 123 123 123 | 123 123 123
                           | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
               #-----------+-------------+------------
                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
               #-----------+-------------+------------
                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
            """
            ))
            self.assertTrue(puzzle.is_equal_to(expected))

            #puzzle.add_CandidateLines()
            CandidateLines.add_to_puzzle(puzzle)

            logging.info("After puzzle.add_CandidateLines:\n" + puzzle.to_string())
            expected.load_candidates_from_string2(dedent(
            """\
               1    2    3 |             |            
                           | 456 456 456 | 456 456 456
                           | 789 789 789 | 789 789 789

                           | 123 123 123 | 123 123 123
               4    5    6 |             |            
                           | 789 789 789 | 789 789 789

                           | 123 123 123 | 123 123 123
                           | 456 456 456 | 456 456 456
               789 789 789 |             |            
               #-----------+-------------+------------
                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
               #-----------+-------------+------------
                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

                23 1 3 12  | 123 123 123 | 123 123 123
                56 4 6 45  | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
            """
            ))
            #import pdb; pdb.set_trace()
            self.assertTrue(puzzle.is_equal_to(expected))

        finally:
            logging.getLogger().setLevel(logging.CRITICAL)

    def test_candidate_lines2(self):
        try:
            puzzle = Puzzle(3)
            CandidateLines.add_to_puzzle(puzzle)
            logging.info("Before set_value(0,0,1):\n" + puzzle.to_string())
            puzzle.get_cell(0, 0).set_value('1')
            logging.info("After set_value(0,0,1):\n" + puzzle.to_string())
            puzzle.get_cell(0, 1).set_value('2')
            logging.info("After set_value(0,1,2):\n" + puzzle.to_string())
            puzzle.get_cell(0, 2).set_value('3')
            puzzle.get_cell(1, 0).set_value('4')
            puzzle.get_cell(1, 1).set_value('5')
            logging.info("After set_value(1,1,5):\n" + puzzle.to_string())
            puzzle.get_cell(1, 2).set_value('6')
            logging.info("After set_value calls:\n" + puzzle.to_string())
            logging.getLogger().setLevel(logging.CRITICAL)
            expected = Puzzle(3)
            expected.load_candidates_from_string2(dedent(
            """\
               1    2    3 | 123 123 123 | 123 123 123
                           | 456 456 456 | 456 456 456
                           | 789 789 789 | 789 789 789

                           | 123 123 123 | 123 123 123
               4    5    6 | 456 456 456 | 456 456 456
                           | 789 789 789 | 789 789 789

               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 |             |            
               #-----------+-------------+------------
               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
               #-----------+-------------+------------
               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789

               123 123 123 | 123 123 123 | 123 123 123
               456 456 456 | 456 456 456 | 456 456 456
               789 789 789 | 789 789 789 | 789 789 789
            """
            ))
            #logging.getLogger().setLevel(logging.INFO)
            logging.info("Puzzle = \n"
                    + puzzle.to_string())
            logging.info("Expected = \n"
                    + expected.to_string())
            #import pdb; pdb.set_trace()
            self.assertTrue(puzzle.is_equal_to(expected))

        finally:
            logging.getLogger().setLevel(logging.CRITICAL)

init_logging()

if __name__ == '__main__':
    unittest.main(verbosity=2)

# The End
# vim:foldmethod=indent:foldnestmax=2
