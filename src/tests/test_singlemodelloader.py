import unittest
import sys
import os
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
from extractmodel import ModelExtractor

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)

class SingleModelLoaderTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        self.form = LogIT.MainGui(False, os.path.join(os.getcwd(), 'settings.logset'))
        self.form.widgets['New Entry'].cur_log_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\Blank_DB.logdb'
        self.form.widgets['New Entry']._TEST_MODE = True

    def test_loadSingleModel(self):
        """
        """
        print 'Made it'
        testpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        self.form.widgets['New Entry'].loadModelTextbox.setText(testpath)
        self.form.widgets['New Entry']._loadSingleLogEntry(testpath)
        all_logs = self.form.widgets['New Entry'].all_logs 
        
        
        
        i=0