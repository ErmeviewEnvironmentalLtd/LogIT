import unittest
import sys
import os
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
from LogBuilder import ModelLoader
import LogClasses

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class LogBuilderTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        pass


    def test_loadModel(self):
        """
        """
        # Make sure it reports lack of ecf file handling properly
        fake_ecfpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\tuflow\runs\fake_ECF.ecf'
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

        # Check we can load an actual model properly 
        testpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(testpath)
        self.assertIsNot(all_logs, False, 'all_logs load fail')
        self.assertTrue(isinstance(all_logs, LogClasses.AllLogs), 'all_logs instance fail')
        self.assertListEqual(model_loader.missing_files, [], 'missing_model_files fail')
        
        # Convert all the dates to the ones in the test data
        for k, v in all_logs.log_pages.iteritems():
            for c in v.contents:
                c['DATE'] = '27/03/2016'
        
        KENNFORD_DICT = self.getKennfordDict()
        for log_key, log in all_logs.log_pages.iteritems():
            self.assertListEqual(KENNFORD_DICT[log_key], log.contents, 'Log contents for %s not equal' % (log_key))
            
            if log_key == 'BC_DBASE' or log_key == 'ECF':
                self.assertFalse(log.has_contents, 'Log %s has_contents fail' % (log_key))
            else:
                self.assertTrue(log.has_contents, 'Log %s has_contents fail' % (log_key))
        
        ief_dir = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\isis\\iefs'
        tcf_dir = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\tuflow\\runs'
        self.assertEqual(ief_dir, all_logs.ief_dir, 'ief_dir fail')
        self.assertEqual(tcf_dir, all_logs.tcf_dir, 'tcf_dir fail')
        
        
    def getKennfordDict(self):
        
        KENNFORD_DICT = {
            'BC_DBASE': [{'BC_DBASE': 'None',
                        'COMMENTS': 'None',
                        'DATE': '27/03/2016',
                        'FILES': 'None'}],
            'DAT': [{'AMENDMENTS': 'None',
                    'COMMENTS': 'None',
                    'DAT': 'kennford_1%AEP_FINAL_v1.17.DAT',
                    'DATE': '27/03/2016'}], 
            'ECF': [{'COMMENTS': 'None', 'DATE': '27/03/2016', 'ECF': 'None', 'FILES': 'None'}],
            'RUN': [{'BC_DBASE': 'None',
                    'COMMENTS': 'None',
                    'DAT': 'kennford_1%AEP_FINAL_v1.17.DAT',
                    'DATE': '27/03/2016',
                    'DESCRIPTION': 'None',
                    'ECF': 'None',
                    'EVENT_DURATION': '14.0',
                    'EVENT_NAME': 'None',
                    'IEF': 'kennford_1%AEP_FINAL_v5.18.ief',
                    'IEF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\isis\\iefs',
                    'ISIS_BUILD': 'None',
                    'MODELLER': 'None',
                    'RESULTS_LOCATION_1D': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18',
                    'RESULTS_LOCATION_2D': '..\\results\\2d\\kennford_1%AEP_FINAL_v5.18\\',
                    'RUN_OPTIONS': 'None',
                    'SETUP': 'None',
                    'TBC': '[kennford_v3.5.tbc]',
                    'TCF': '[kennford_1%AEP_FINAL_v5.18.tcf]',
                    'TCF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\tuflow\\runs',
                    'TGC': '[kennford_v5.9.tgc]',
                    'TUFLOW_BUILD': 'None'}],
            'TBC': [{'COMMENTS': 'None',
                    'DATE': '27/03/2016',
                    'FILES': ['kennford_2d_bc_ALL_v4.5.mif'],
                    'TBC': 'kennford_v3.5.tbc'}],
            'TCF': [{'COMMENTS': 'None',
                    'DATE': '27/03/2016',
                    'FILES': ['Projection.mif',
                            'Materials.csv',
                            'kennford_1d_nodes_v3.3.mif',
                            'Kennford_1d_nwk_v1.0.mif',
                            'Kennford_1d_WLL_v1.0.mif',
                            'kennford_v5.9.tgc',
                            'kennford_v3.5.tbc',
                            'Kennford_2d_po_DefLB_v2.0.mif',
                            'Kennford_2d_po_DefRB_v1.0.mif',
                            'Kennford_2d_po_DefLB_USB_v1.0.mif',
                            'Kennford_2d_po_DefRB_USB_v1.0.mif'],
                    'TCF': 'kennford_1%AEP_FINAL_v5.18.tcf'}],
            'TGC': [{'COMMENTS': 'None',
                    'DATE': '27/03/2016',
                    'FILES': ['kennford_2d_code_v1.0.mif',
                            'kennford_2d_bc_ALL_v4.5.mif',
                            'Kennford_DTM.txt',
                            'kennford_2d_za_buildings_ALL_v2.0.mif',
                            'kennford_2d_bc_ALL_v4.5.mif',
                            'kennford_2d_zpt_rivers_v3.1.mif',
                            'kennford_2d_zln_defLB_v1.0.mif',
                            'kennford_2d_zln_defRB_v1.0.mif',
                            'kennford_2d_zln_bridge_v2.0.mif',
                            'kennford_2d_mat_v2.0.mif',
                            'kennford_2d_mat_Buildings_v1.0.mif'],
                    'TGC': 'kennford_v5.9.tgc'}]
            } 
        return KENNFORD_DICT
        