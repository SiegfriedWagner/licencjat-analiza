import unittest as ut
import pandas as pd
from csv_parser import *
from os.path import join, dirname

class TestSetVolume(ut.TestCase):

    def setUp(self):
        input = join(dirname(__file__), 'SetVideo.csv')
        task_path = join(dirname(__file__), 'SetVideo.txt')
        self.parsed = parse_csv(TaskAnalyzer, task_path, input)

    def test_task_name(self):
        self.assertEqual(self.parsed['Task name'][0], 'SetPanelAndVideo')

    def test_number_of_errors(self):
        self.assertEqual(self.parsed['Number of errors'].values[0], 1)

    def test_completed(self):
        self.assertEqual(self.parsed['Completed'].values[0], True)

    def test_shape(self):
        self.assertEqual(self.parsed.shape[0], 1)