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
        settings = LogIT.LogitSettings()
        settings.cur_settings_path = os.path.join(os.getcwd(), 'settings.logset')
        self.form = LogIT.MainGui(LogIT.LogitSettings())
        self.blank_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\Blank_DB.logdb'
        self.testpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'


    def test_fetchAndCheckModel(self):
        """
        """
        fakepath = r'C:\Fake\Path\to\Nonexistant\model.ief'
        kennford_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\Kennford_entry.logdb'
        
        # Test with an empty database and real model
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = self.blank_db
        errors, all_logs = Controller.fetchAndCheckModel(self.testpath, {}, errors)
        self.assertFalse(errors.has_errors, 'Found error in fetch fail')
        
        # Test with a fake model path
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = self.blank_db
        errors, all_logs = Controller.fetchAndCheckModel(fakepath, {}, errors)
        self.assertTrue(errors.has_errors, 'fake model error in fetch fail')
        e = errors.log[-1]
        self.assertEqual(e.title, errors.MODEL_LOAD, 'fake model error type fail')
        
        # Test with model already in database
        errors = GuiStore.ErrorHolder()
        self.form.settings.cur_log_path = self.blank_db
        errors, all_logs = Controller.fetchAndCheckModel( self.testpath, {}, errors)
        self.assertTrue(errors.has_errors, 'existing model error in fetch fail')
        e = errors.log[-1]
        self.assertEqual(e.title, errors.LOG_EXISTS, 'fake model error type fail')
    
    
    def test_getRunStatusInfo(self):
        """
        """
#         tcf_dir = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\tuflow\runs'
#         kenn_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
#         errors = GuiStore.ErrorHolder()
#         errors, all_logs = Controller.fetchAndCheckModel(self.blank_db, self.testpath, errors)
        
        tcf_name = 'kennford_1%AEP_FINAL_v5.18.tcf'
        tcf_dir = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\tuflow\runs'
        
        outputs = Controller.getRunStatusInfo(tcf_dir, tcf_name, '')
        self.assertTrue(outputs[0], 'Run Status Info success True fail')
        self.assertEqual(outputs[1], 'Finished', 'Run Status Info Finished status fail')
        self.assertEqual(outputs[2], '0.17', 'Run Status Info Finished MB status fail')
        
#         run_log = all_logs.getLogEntryContents('RUN', 0)
#         self.assertEqual(run_log['RUN_STATUS'], 'Finished')
#         self.assertEqual(run_log['MB'], '0.17')
        
        
        