import unittest
import sys
import os
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
from runsummary import RunSummary

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class RunSummaryTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        self.form = LogIT.MainGui(False, os.path.join(os.getcwd(), 'settings.logset'))
        self.summary = self.form.widgets['Run Summary']
    
    
    def test_getHoursFromDateStr(self):
        """
        """
        test_time1 = '3:15:00'
        test_time2 = '13:45:00'
        hours1, time = self.summary.getHoursFromDateStr(test_time1)
        hours2, time = self.summary.getHoursFromDateStr(test_time2)
        self.assertEqual(hours1, 3.25, 'hours1 equality test fail')
        self.assertEqual(hours2, 13.75, 'hours2 equality test fail')