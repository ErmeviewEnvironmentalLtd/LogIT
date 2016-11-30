import unittest
import sys
import os
import json

from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
import LogBuilder
from LogBuilder import ModelLoader
import LogClasses

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class LogBuilderTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        # Get kenn file
        kenfile = r"C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\json\kenfile.json"
        with open(kenfile, 'rb') as f:
            self.kenn_data = json.load(f)
        
        # Get gos file
        gosfile = r"C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\json\gosfile.json"
        with open(gosfile, 'rb') as f:
            self.gos_data = json.load(f)
        
        # Get 1d file
        onedfile = r"C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\json\1dfile.json"
        with open(onedfile, 'rb') as f:
            self.oned_data = json.load(f)


    def test_loadModel(self):
        """
        """
        # Make sure it reports lack of ecf file handling properly
        fake_ecfpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\Kennford\tuflow\runs\Fake_ECF.ecf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(fake_ecfpath)
        self.assertFalse(all_logs, 'all_logs ecf load fail')
        self.assertEqual(model_loader.error, 'Cannot currently load an ecf file as the main file')
         
        # Check we handle non existant files properly
        fakepath = r'C:\Some\fake\file\path.tcf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(fakepath)
        self.assertFalse(all_logs, 'all_logs fake path load fail')
        self.assertEqual(model_loader.error, 'File does not exist')
 
        # Check that we can find missing files correctly
        gos_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\GoS\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01_MissingTgc.tcf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(gos_path)
        self.assertFalse(all_logs, 'all_logs load fail')
        self.assertEqual(model_loader.error, 'Some key model files could not be found during load')
        test_files = [
            "C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Loader\\model\\GoS\\tuflow\\model\\Grange_baseline_Option1A_v1-00_Fake.tgc"
        ]
        self.assertListEqual(model_loader.missing_files, test_files, 'GoS missing_model_files fail')
 
 
        '''
            KENNFORD MODEL
        '''
        kenn_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(kenn_path)
        self.assertIsNot(all_logs, False, 'all_logs load fail')
        self.assertTrue(isinstance(all_logs, LogClasses.AllLogs), 'all_logs instance fail')
        self.assertListEqual(model_loader.missing_files, [], 'missing_model_files fail')

        # Check the loaded data
        kenn_logs = all_logs.jsonify()
        self.assertListEqual(kenn_logs['models'], self.kenn_data['models'])
        self.assertListEqual(kenn_logs['ieds'], self.kenn_data['ieds'])
        self.assertDictEqual(kenn_logs['run'], self.kenn_data['run'])
        self.assertDictEqual(kenn_logs['dat'], self.kenn_data['dat'])
        self.assertListEqual(kenn_logs['editing_allowed'], self.kenn_data['editing_allowed'])
        self.assertEqual(kenn_logs['ief_dir'], self.kenn_data['ief_dir'])
        self.assertEqual(kenn_logs['tcf_dir'], self.kenn_data['tcf_dir'])
        self.assertEqual(kenn_logs['run_filename'], self.kenn_data['run_filename'])
        self.assertEqual(kenn_logs['run_hash'], self.kenn_data['run_hash'])

        
        '''
            GOS MODEL
        '''
        gos_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\GoS\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.tcf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(gos_path)
        self.assertIsNot(all_logs, False, 'all_logs load fail')
        self.assertTrue(isinstance(all_logs, LogClasses.AllLogs), 'all_logs instance fail')
        self.assertListEqual(model_loader.missing_files, [], 'missing_model_files fail')

        # Check the loaded data
        gos_logs = all_logs.jsonify()
        self.assertListEqual(gos_logs['models'], self.gos_data['models'])
        self.assertListEqual(gos_logs['ieds'], self.gos_data['ieds'])
        self.assertDictEqual(gos_logs['run'], self.gos_data['run'])
        self.assertEqual(gos_logs['dat'], self.gos_data['dat'])
        self.assertListEqual(gos_logs['editing_allowed'], self.gos_data['editing_allowed'])
        self.assertEqual(gos_logs['ief_dir'], self.gos_data['ief_dir'])
        self.assertEqual(gos_logs['tcf_dir'], self.gos_data['tcf_dir'])
        self.assertEqual(gos_logs['run_filename'], self.gos_data['run_filename'])
        self.assertEqual(gos_logs['run_hash'], self.gos_data['run_hash'])
        
        
        '''
            1D ONLY MODEL
        '''
        oned_path = r"C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\1d_only\kennford_1%AEP_FINAL_v5.18.ief"
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(oned_path)
        self.assertIsNot(all_logs, False, 'all_logs load fail')
        self.assertTrue(isinstance(all_logs, LogClasses.AllLogs), 'all_logs instance fail')
        
#         self.jsonifyTestModel(oned_path, r"C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\json\1dfile.json")
#         return

        # Check the loaded data
        oned_logs = all_logs.jsonify()
        self.assertListEqual(oned_logs['models'], self.oned_data['models'])
        self.assertListEqual(oned_logs['ieds'], self.oned_data['ieds'])
        self.assertDictEqual(oned_logs['run'], self.oned_data['run'])
        self.assertEqual(oned_logs['dat'], self.oned_data['dat'])
        self.assertListEqual(oned_logs['editing_allowed'], self.oned_data['editing_allowed'])
        self.assertEqual(oned_logs['ief_dir'], self.oned_data['ief_dir'])
        self.assertEqual(oned_logs['tcf_dir'], self.oned_data['tcf_dir'])
        self.assertEqual(oned_logs['run_filename'], self.oned_data['run_filename'])
        self.assertEqual(oned_logs['run_hash'], self.oned_data['run_hash'])
        
        
    
    def jsonifyTestModel(self, model_path, json_path):
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(model_path)
        output = all_logs.jsonify()
 
        with open(json_path, 'wb') as f:
            json.dump(output, f)
        
    