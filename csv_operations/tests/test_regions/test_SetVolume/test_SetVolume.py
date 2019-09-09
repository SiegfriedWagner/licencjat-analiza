import unittest as ut
import pandas as pd
from csv_parser import *
from os.path import join, dirname

class TestSetVolume(ut.TestCase):

    def setUp(self):
        input = join(dirname(__file__), 'SetVolume.csv')
        task_path = join(dirname(__file__), 'SetVolume.txt')
        self.parsed = parse_csv(RegionsTaskAnalyzer, task_path, input, subtasks=True)

    def test_task_name(self):
        self.assertEqual(self.parsed['Task name'].values[0], 'ReduceVolume')

    def test_set_time_shape(self):
        self.assertEqual(self.parsed.shape[0], 3)

    def test_set_time_errors(self):
        self.assertEqual(self.parsed['Number of errors'].values[0], 0)
        self.assertEqual(self.parsed['Number of errors'].values[1], 0)
        self.assertEqual(self.parsed['Number of errors'].values[2], 0)

    def test_set_time_completed(self):
        self.assertEqual(self.parsed['Completed'].values[0], True)
        self.assertEqual(self.parsed['Completed'].values[1], True)
        self.assertEqual(self.parsed['Completed'].values[2], True)