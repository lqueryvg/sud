#!/usr/bin/env python2

import sud2
import unittest


class TestCandidateSet(unittest.TestCase):
    def test_constructor_zero_elements(self):
        self.assertRaises(sud2.AtLeastTwoCandidateValuesRequired,
                          sud2.CandidateSet, [])

    def test_constructor_one_element(self):
        self.assertRaises(sud2.AtLeastTwoCandidateValuesRequired,
                          sud2.CandidateSet, ["one"])

    def test_remove_candidate(self):
        obj = sud2.CandidateSet([1, 3, 2])
        obj.remove(2)
        self.assertFalse(2 in obj)
        self.assertTrue(1 in obj)
        self.assertTrue(3 in obj)

    def test_remove_final_candidate(self):
        obj = sud2.CandidateSet([1, 2])
        try:
            obj.remove(1)
        except:
            pass
        self.assertRaises(sud2.RemoveOnlyCandidate, obj.remove, 2)

    def test_remove_OneCandidateRemains(self):
        obj = sud2.CandidateSet([1, 2])
        self.assertRaises(sud2.OneCandidateRemains, obj.remove, 2)

    def test_remove_ValueError_on_remove_element_not_there(self):
        obj = sud2.CandidateSet([1, 2])
        self.assertRaises(KeyError, obj.remove, 3)


class TestCell(unittest.TestCase):
    def test_set_then_get(self):
        cell = sud2.Cell([1, 2, 3])
        cell.set_value(1)
        self.assertTrue(cell.get_value() == 1)

    def test_set_value_already_set(self):
        cell = sud2.Cell([1, 2, 3])
        cell.set_value(1)
        self.assertRaises(sud2.CellAlreadySet, cell.set_value, 1)

    def test_set_value_not_a_candidate(self):
        cell = sud2.Cell([1, 2])
        self.assertRaises(sud2.ValueIsNotACandidate, cell.set_value, 3)


class TestConstraintGroup(unittest.TestCase):
    def test_notify(self):
        cell1 = sud2.Cell([1, 2])
        cell2 = sud2.Cell([1, 2])
        grp = sud2.ConstraintGroup([cell1, cell2])
        cell1.set_value(1)
        self.assertTrue(cell2.get_value() == 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
