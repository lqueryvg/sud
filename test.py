#!/usr/bin/env python2

import sud2
import unittest

class TestCandidateSet(unittest.TestCase):
    def test_exception_constructor_with_zero_elements(self):
        with self.assertRaises(Exception) as cm:
            obj = sud2.CandidateSet([])
        self.assertEqual(cm.exception.args[0], "need >1 element to init candidate set")

    def test_exception_constructor_with_one_element(self):
        with self.assertRaises(Exception) as cm:
            obj = sud2.CandidateSet(["one"])
        self.assertEqual(cm.exception.args[0], "need >1 element to init candidate set")

#    def test_exception_remove_only_1_element_remains(self):
#        with self.assertRaises(Exception) as cm:
#            obj = sud2.CandidateSet([1,2])
#            obj.remove(2)
#        self.assertEqual(cm.exception.args[0], "only 1 candidate remains")

    def test_remove_element(self):
        obj = sud2.CandidateSet([1,3,2])
        obj.remove(2)
        self.assertFalse(2 in obj)

    def test_exception_attempt_to_remove_final_element(self):
        obj = sud2.CandidateSet([1,2])
        try:
            obj.remove(1)
        except:
            pass
        with self.assertRaises(Exception) as cm:
            obj.remove(2)
        self.assertEqual(cm.exception.args[0],
                "attempt to remove final candidate")

    def test_exception_LastCandidate(self):
        obj = sud2.CandidateSet([1,2])
        self.assertRaises(sud2.LastCandidate, obj.remove, 2)

    def test_exception_ValueError_on_remove_element_not_there(self):
        obj = sud2.CandidateSet([1,2])
        self.assertRaises(KeyError, obj.remove, 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)
