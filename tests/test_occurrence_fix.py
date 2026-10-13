"""
test_occurrence_fix.py — Prove repeated phrases anchor to correct occurrence.
"""
import unittest
import sys
sys.path.insert(0, "tools")
from generate_event_timeline import find_word_anchor

class TestOccurrence(unittest.TestCase):
    def setUp(self):
        # Words with repeated phrase "pay your bills"
        self.words = [
            {"word": "pay", "start": 0.0, "end": 0.3},
            {"word": "your", "start": 0.3, "end": 0.5},
            {"word": "bills", "start": 0.5, "end": 0.8},
            {"word": "and", "start": 0.8, "end": 1.0},
            {"word": "pay", "start": 1.0, "end": 1.3},
            {"word": "your", "start": 1.3, "end": 1.5},
            {"word": "bills", "start": 1.5, "end": 1.8},
        ]
    
    def test_first_occurrence(self):
        idx, matched = find_word_anchor(self.words, "pay your bills", occurrence=1)
        self.assertEqual(idx, 0)
        self.assertEqual(matched, "pay your bills")
    
    def test_second_occurrence(self):
        idx, matched = find_word_anchor(self.words, "pay your bills", occurrence=2)
        self.assertEqual(idx, 4)
        self.assertEqual(matched, "pay your bills")
    
    def test_default_is_first(self):
        idx, matched = find_word_anchor(self.words, "pay your bills")
        self.assertEqual(idx, 0)
    
    def test_occurrence_out_of_range(self):
        idx, matched = find_word_anchor(self.words, "pay your bills", occurrence=3)
        self.assertIsNone(idx)

if __name__ == "__main__":
    unittest.main()
