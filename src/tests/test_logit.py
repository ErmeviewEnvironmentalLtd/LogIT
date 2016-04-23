import unittest
import sys
import os
import shutil
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
import Controller
import GuiStore

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class LogitTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        self.form = LogIT.MainGui(False, os.path.join(os.getcwd(), 'settings.logset'))
        self.new_entry = self.form.widgets['New Entry']
        self.form._TEST_MODE = True
        self.new_entry._TEST_MODE = True
        self.blank_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\temp\Blank_DB.logdb'
        self.kenn_db = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases\temp\Kennford_Server.logdb'
        self.setupTestDatabases()
    
    
    def tearDown(self):
        """
        """
        os.remove(self.blank_db)
        os.remove(self.kenn_db)
    
    
    def testMultipleLoad(self):
        """
        """
        test_paths = [r'P:\00 Project Files\13059 EA SW Consultancy Support\Technical\Kennford_model\model\hydraulics\Final_Model\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief',
                      r'P:\00 Project Files\13059 EA SW Consultancy Support\Technical\Kennford_model\model\hydraulics\Final_Model\model\isis\iefs\kennford_1%AEP_FINAL_v5.18_brgCoef-20%.ief',
                      r'P:\00 Project Files\13059 EA SW Consultancy Support\Technical\Kennford_model\model\hydraulics\Final_Model\model\isis\iefs\kennford_1%AEP_FINAL_v5.18_dsbd-20%.ief'
                     ]
        
        # Setup the model paths and database for the blank run
        self.new_entry._updateMultipleLogSelection('addMultiModelButton', test_paths)
        
        # Check we get the same file paths back that we put in and hand the
        # blank database path over
        model_paths = self.new_entry.getMultipleModelPaths()
        self.assertListEqual(test_paths, model_paths, 'Input output model path equality fail')
        self.form.settings.cur_log_path = self.blank_db
        
        # Check that all goes well with adding the new entries
        errors = self.form._createMultipleLogEntry()
        self.assertFalse(errors.has_errors, 'Blank DB has_error fail')
        
        # Check what happens when we try to load a model with an error
        error_path = [r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\GoS\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01_MissingTgc.tcf']
        self.new_entry._updateMultipleLogSelection('addMultiModelButton', error_path)
        model_paths = self.new_entry.getMultipleModelPaths()
        self.assertListEqual(error_path, model_paths, 'Input output error_path equailty fail')
        errors = self.form._createMultipleLogEntry()
        self.assertTrue(errors.has_errors, 'error_path has error fail')
        error_title = 'Model Load Error'
        error_msg = ('Unable to load model log from file  at:\nC:\\Users\\' +
                     'duncan.runnacles\\Documents\\Programming\\Python\\' +
                     'LogITApp\\Regression_Test_Data\\Loader\\model\\GoS\\' +
                     'tuflow\\runs\\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01_MissingTgc.tcf' +
                     '\n\nThe following tuflow model files could not be loaded:\nGrange_baseline_Option1A_v1-00_Fake.tgc')
        self.assertEqual(error_title, errors.log[0].title, 'error_path errors title fail')
        self.assertEqual(error_msg, errors.log[0].message, 'error_path errors message fail')
        
        # Set to the non blank database
        self.new_entry._updateMultipleLogSelection('addMultiModelButton', test_paths)
        model_paths = self.new_entry.getMultipleModelPaths()
        self.assertListEqual(test_paths, model_paths, 'Input output model path equality fail')
        self.form.settings.cur_log_path = self.kenn_db
        
        # Make sure we get some errors for trying to load an existing model
        errors = self.form._createMultipleLogEntry()
        self.assertTrue(errors.has_errors, 'Kenn DB has_error fail')
        error_title = 'Log Entry Exists Error'
        error0_msg = 'Selected file already exists in database :\nfile = P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\iefs\\kennford_1%AEP_FINAL_v5.18.ief'
        error1_msg = 'Selected file already exists in database :\nfile = P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\iefs\\kennford_1%AEP_FINAL_v5.18_dsbd-20%.ief'
        self.assertEqual(error_title, errors.log[0].title, 'Kenn DB Recorded errors title 0 fail')
        self.assertEqual(error_title, errors.log[1].title, 'Kenn DB Recorded errors title 1 fail')
        self.assertEqual(error0_msg, errors.log[0].message, 'Kenn DB Recorded errors message 0 fail')
        self.assertEqual(error1_msg, errors.log[1].message, 'Kenn DB Recorded errors message 1 fail')
        
    
    def setupTestDatabases(self):
        """
        """
        db_folder = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\databases'
        shutil.copyfile(os.path.join(db_folder, 'Blank_DB.logdb'), os.path.join(db_folder, 'temp', 'Blank_DB.logdb'))
        shutil.copyfile(os.path.join(db_folder, 'Kennford_Server.logdb'), os.path.join(db_folder, 'temp', 'Kennford_Server.logdb'))

        

