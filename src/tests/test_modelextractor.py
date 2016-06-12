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


class ModelExtractorTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        settings = LogIT.LogitSettings()
        settings.cur_settings_path = os.path.join(os.getcwd(), 'settings.logset')
        self.form = LogIT.MainGui(LogIT.LogitSettings())
        self.extractor = self.form.widgets['Model Extractor']
    
    
    def test_extractModel(self):
        """
        """
        in_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        out_dir = r'C:\Some\fake\folder'
        
        success, tuflow_files = self.extractor._extractModelSetup(in_path, out_dir)
        
        vars = self.extractor._extractVars
        
        self.assertListEqual(vars.failed_data_files, ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\Materials.csv'], 'failed_data_files equality fail')
        self.assertTrue(vars.has_tcf, 'has_tcf fail')
        self.assertListEqual(vars.in_files, self.getInFilesCheck(), 'in_files equality fail')
        self.assertListEqual(vars.out_files, self.getOutFilesCheck(), 'in_files equality fail')
        self.assertListEqual(vars.results_files, self.getResultsFilesCheck(), 'in_files equality fail')
    
    
    def test_checkIfRightFile(self):
        """
        """
        run_name = 'MY_SUPERSPECIAL_RUN_V1.0'
        
        # Ones that should get through
        isis_result = run_name + '.ZZN'
        tuflow_result = run_name + '.ALL.SUP'
        tuflow_result2 = run_name + '_ZUK1.DAT'
        tuflow_check_normal = run_name + '_DOM_CHECK.MIF'
        tuflow_check_prefix = 'someprefix_' + '_ZUK1.DAT'
        tuflow_log = run_name + '.TLF'
        self.assertTrue(self.extractor.checkIfRightFile(run_name, isis_result), 'isis result fail')
        self.assertTrue(self.extractor.checkIfRightFile(run_name, tuflow_result), 'tuflow result fail')
        self.assertTrue(self.extractor.checkIfRightFile(run_name, tuflow_result2), 'tuflow result2 fail')
        self.assertTrue(self.extractor.checkIfRightFile(run_name, tuflow_check_normal), 'tuflow check_normal fail')
        self.assertTrue(self.extractor.checkIfRightFile(run_name, tuflow_log), 'tuflow log fail')
        self.assertTrue(self.extractor.checkIfRightFile('someprefix_', tuflow_check_prefix), 'tuflow check_prefix fail')
        
        # And some that shouldn't
        wrong_name = 'MY_SUPERSPECIAL_RUN_V1.6' 
        isis_result = wrong_name + '.ZZN'
        tuflow_result = wrong_name + '.ALL.SUP'
        tuflow_result2 = wrong_name + '_ZUK1.DAT'
        tuflow_check_normal = wrong_name + '_DOM_CHECK.MIF'
        tuflow_log = wrong_name + '.TLF'
        self.assertFalse(self.extractor.checkIfRightFile(run_name, isis_result), 'isis result fail')
        self.assertFalse(self.extractor.checkIfRightFile(run_name, tuflow_result), 'tuflow result fail')
        self.assertFalse(self.extractor.checkIfRightFile(run_name, tuflow_result2), 'tuflow result2 fail')
        self.assertFalse(self.extractor.checkIfRightFile(run_name, tuflow_check_normal), 'tuflow check_normal fail')
        self.assertFalse(self.extractor.checkIfRightFile(run_name, tuflow_log), 'tuflow log fail')
        self.assertFalse(self.extractor.checkIfRightFile('', tuflow_check_prefix), 'tuflow check_prefix fail')
        
    
    
    def getResultsFilesCheck(self):
        RESULTS_FILES_CHECK = [['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18',
                                  'C:\\Some\\fake\\folder\\fmp\\results\\KENNFORD_1%AEP_FINAL_V5.18'],
                                 ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\Log\\kennford_1%AEP_FINAL_v5.18',
                                  'C:\\Some\\fake\\folder\\tuflow\\runs\\logs\\kennford_1%AEP_FINAL_v5.18'],
                                 ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\results\\2d\\kennford_1%AEP_FINAL_v5.18\\kennford_1%AEP_FINAL_v5.18',
                                  'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\results\\2d\\kennford_1%AEP_FINAL_v5.18'],
                                 ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\check\\2d\\kennford_1%AEP_FINAL_v5.18\\kennford_1%AEP_FINAL_v5.18',
                                  'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\checks\\kennford_1%AEP_FINAL_v5.18']]
        return RESULTS_FILES_CHECK
        
        
    def getOutFilesCheck(self):
        OUT_FILES_CHECK = ['C:\\Some\\fake\\folder\\fmp\\dats\\kennford_1%AEP_FINAL_v1.17.DAT',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Projection.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Projection.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_1d_nodes_v3.3.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_1d_nodes_v3.3.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_1d_nwk_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_1d_nwk_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_1d_WLL_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_1d_WLL_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefLB_v2.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefLB_v2.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefRB_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefRB_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefLB_USB_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefLB_USB_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefRB_USB_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\Kennford_2d_po_DefRB_USB_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\Materials.csv',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_code_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_code_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\grid\\Kennford_DTM.txt',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_za_buildings_ALL_v2.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_za_buildings_ALL_v2.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zpt_rivers_v3.1.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zpt_rivers_v3.1.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_defLB_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_defLB_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_defRB_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_defRB_v1.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_bridge_v2.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_zln_bridge_v2.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_mat_v2.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_mat_v2.0.mid',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_mat_Buildings_v1.0.mif',
                             'C:\\Some\\fake\\folder\\tuflow\\runs\\..\\model\\gis\\kennford_2d_mat_Buildings_v1.0.mid']
        return OUT_FILES_CHECK
        
        
    def getInFilesCheck(self):
        IN_FILES_CHECK = ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Projection.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Projection.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\kennford_1d_nodes_v3.3.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\kennford_1d_nodes_v3.3.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_1d_nwk_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_1d_nwk_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_1d_WLL_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_1d_WLL_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefLB_v2.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefLB_v2.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefRB_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefRB_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefLB_USB_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefLB_USB_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefRB_USB_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\mi\\Kennford_2d_po_DefRB_USB_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\Materials.csv',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_code_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_code_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\grid\\Kennford_DTM.txt',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_za_buildings_ALL_v2.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_za_buildings_ALL_v2.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zpt_rivers_v3.1.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zpt_rivers_v3.1.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_defLB_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_defLB_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_defRB_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_defRB_v1.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_bridge_v2.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_zln_bridge_v2.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_mat_v2.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_mat_v2.0.mid',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_mat_Buildings_v1.0.mif',
                         'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\..\\model\\..\\model\\mi\\kennford_2d_mat_Buildings_v1.0.mid']
        return IN_FILES_CHECK
        
        
    