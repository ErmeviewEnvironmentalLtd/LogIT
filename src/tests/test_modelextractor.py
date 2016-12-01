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
        in_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        out_dir = r'C:\Some\fake\folder'
         
        success, tuflow_files = self.extractor._extractModelSetup(in_path, out_dir, '')
         
        vars = self.extractor._extractVars
        failed_list = ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\Materials.csv']
        self.assertListEqual(vars.failed_data_files, failed_list, 'failed_data_files equality fail')
        self.assertTrue(vars.has_tcf, 'has_tcf fail')
        ifiles = self.getInFilesCheck()
        self.assertEqual(set(vars.in_files), set(self.getInFilesCheck()), 'in_files equality fail')
        self.assertEqual(set(vars.out_files), set(self.getOutFilesCheck()), 'out_files equality fail')
        for r in self.getResultsFilesCheck():
            self.assertTrue(r in vars.results_files)
     
     
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
        RESULTS_FILES_CHECK = [
            ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18',
            'C:\\Some\\fake\\folder\\fmp\\results\\KENNFORD_1%AEP_FINAL_V5.18'],
            ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\Log\\kennford_1%AEP_FINAL_v5.18',
            'C:\\Some\\fake\\folder\\tuflow\\runs\\logs\\kennford_1%AEP_FINAL_v5.18'],
            ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\results\\2d\\kennford_1%AEP_FINAL_v5.18\\kennford_1%AEP_FINAL_v5.18',
            'C:\\Some\\fake\\folder\\tuflow\\results\\2d\\kennford_1%AEP_FINAL_v5.18'],
            ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\check\\2d\\kennford_1%AEP_FINAL_v5.18\\kennford_1%AEP_FINAL_v5.18',
            'C:\\Some\\fake\\folder\\tuflow\\checks\\kennford_1%AEP_FINAL_v5.18']
        ]
        return RESULTS_FILES_CHECK
         
         
    def getOutFilesCheck(self):
        OUT_FILES_CHECK = [
            'C:\\Some\\fake\\folder\\fmp\\dats\\kennford_1%AEP_FINAL_v1.17.DAT',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_code_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_code_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\grid\\Kennford_DTM.txt',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_za_buildings_ALL_v2.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_za_buildings_ALL_v2.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zpt_rivers_v3.1.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zpt_rivers_v3.1.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_defLB_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_defLB_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_defRB_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_defRB_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_bridge_v2.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_zln_bridge_v2.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_mat_v2.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_mat_v2.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_mat_Buildings_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_mat_Buildings_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Projection.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Projection.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_1d_nodes_v3.3.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_1d_nodes_v3.3.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_1d_nwk_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_1d_nwk_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_1d_WLL_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_1d_WLL_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefLB_v2.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefLB_v2.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefRB_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefRB_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefLB_USB_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefLB_USB_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefRB_USB_v1.0.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\Kennford_2d_po_DefRB_USB_v1.0.mid',
            'C:\\Some\\fake\\folder\\tuflow\\model\\Materials.csv',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Some\\fake\\folder\\tuflow\\model\\gis\\kennford_2d_bc_ALL_v4.5.mid'
        ]
        return OUT_FILES_CHECK
         
         
    def getInFilesCheck(self):
        IN_FILES_CHECK = [ 
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_code_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_code_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\grid\\Kennford_DTM.txt',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_za_buildings_ALL_v2.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_za_buildings_ALL_v2.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zpt_rivers_v3.1.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zpt_rivers_v3.1.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_defLB_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_defLB_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_defRB_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_defRB_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_bridge_v2.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_zln_bridge_v2.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_mat_v2.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_mat_v2.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_mat_Buildings_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_mat_Buildings_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Projection.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Projection.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_1d_nodes_v3.3.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_1d_nodes_v3.3.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_1d_nwk_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_1d_nwk_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_1d_WLL_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_1d_WLL_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefLB_v2.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefLB_v2.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefRB_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefRB_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefLB_USB_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefLB_USB_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefRB_USB_v1.0.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\Kennford_2d_po_DefRB_USB_v1.0.mid',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\Materials.csv',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mif',
            'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogIT\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\model\\mi\\kennford_2d_bc_ALL_v4.5.mid'
        ]
        return IN_FILES_CHECK