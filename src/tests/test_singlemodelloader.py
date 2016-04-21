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
        testpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        self.form.widgets['New Entry'].loadModelTextbox.setText(testpath)
        self.form.widgets['New Entry']._loadSingleLogEntry(testpath)
        all_logs = self.form.widgets['New Entry'].all_logs 
        
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
                    'EVENT_NAME': '',
                    'IEF': 'kennford_1%AEP_FINAL_v5.18.ief',
                    'IEF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\isis\\iefs',
                    'ISIS_BUILD': '',
                    'MODELLER': '',
                    'RESULTS_LOCATION_1D': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18',
                    'RESULTS_LOCATION_2D': '..\\results\\2d\\kennford_1%AEP_FINAL_v5.18\\',
                    'RUN_OPTIONS': 'None',
                    'SETUP': 'None',
                    'TBC': '[kennford_v3.5.tbc]',
                    'TCF': '[kennford_1%AEP_FINAL_v5.18.tcf]',
                    'TCF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\tuflow\\runs',
                    'TGC': '[kennford_v5.9.tgc]',
                    'TUFLOW_BUILD': ''}],
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
        