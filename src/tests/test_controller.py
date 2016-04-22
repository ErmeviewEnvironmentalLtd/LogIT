import unittest
import sys
import os
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
import Controller
import GuiStore

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class ControllerTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        self.form = LogIT.MainGui(False, os.path.join(os.getcwd(), 'settings.logset'))


    def test_fetchAndCheckModel(self):
        """
        """
        testpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        fakepath = r'C:\Fake\Path\to\Nonexistant\model.ief'
        blank_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\Blank_DB.logdb'
        kennford_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\Kennford_entry.logdb'
        
        # Test with an empty database and real model
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = blank_db
        errors, all_logs = Controller.fetchAndCheckModel(blank_db, testpath, errors)
        self.assertFalse(errors.has_errors, 'Found error in fetch fail')
        
        # Test with a fake model path
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = blank_db
        errors, all_logs = Controller.fetchAndCheckModel(blank_db, fakepath, errors)
        self.assertTrue(errors.has_errors, 'fake model error in fetch fail')
        e = errors.log[-1]
        self.assertEqual(e.title, errors.MODEL_LOAD, 'fake model error type fail')
        
        # Test with model already in database
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = blank_db
        errors, all_logs = Controller.fetchAndCheckModel(kennford_db, testpath, errors)
        self.assertTrue(errors.has_errors, 'existing model error in fetch fail')
        e = errors.log[-1]
        self.assertEqual(e.title, errors.LOG_EXISTS, 'fake model error type fail')
        
        
        