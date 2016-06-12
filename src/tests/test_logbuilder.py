import unittest
import sys
import os
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
        pass


    def test_loadModel(self):
        """
        """
        # Make sure it reports lack of ecf file handling properly
        fake_ecfpath = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\tuflow\runs\Fake_ECF.ecf'
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
        gos_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\GoS\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01_MissingTgc.tcf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(gos_path)
        self.assertFalse(all_logs, 'all_logs load fail')
        self.assertEqual(model_loader.error, 'Some key model files could not be found during load')
        self.assertListEqual(model_loader.missing_files, ['Grange_baseline_Option1A_v1-00_Fake.tgc'], 'GoS missing_model_files fail')


        '''
            KENNFORD MODEL
        '''
        # Check we can load an actual model properly 
        kenn_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\Kennford\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(kenn_path)
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
            
            if log_key == 'BC_DBASE' or log_key == 'ECF' or log_key == 'TEF':
                self.assertFalse(log.has_contents, 'Log %s has_contents fail' % (log_key))
            else:
                self.assertTrue(log.has_contents, 'Log %s has_contents fail' % (log_key))
        
        ief_dir = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\iefs'
        tcf_dir = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs'
        self.assertEqual(ief_dir, all_logs.ief_dir, 'ief_dir fail')
        self.assertEqual(tcf_dir, all_logs.tcf_dir, 'tcf_dir fail')
        
        
        '''
            GOS MODEL
        '''
        gos_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Loader\model\GoS\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.tcf'
        model_loader = ModelLoader()
        all_logs = model_loader.loadModel(gos_path)
        self.assertIsNot(all_logs, False, 'all_logs load fail')
        self.assertTrue(isinstance(all_logs, LogClasses.AllLogs), 'all_logs instance fail')
        self.assertListEqual(model_loader.missing_files, [], 'GoS missing_model_files fail')
        
        # Convert all the dates to the ones in the test data
        for k, v in all_logs.log_pages.iteritems():
            for c in v.contents:
                c['DATE'] = '27/03/2016'
        
        GOS_DICT = self.getGosDict()
        for log_key, log in all_logs.log_pages.iteritems():
            self.assertListEqual(GOS_DICT[log_key], log.contents, 'Log contents for %s not equal' % (log_key))
            
            if log_key == 'DAT' or log_key == 'TEF':
                self.assertFalse(log.has_contents, 'Log %s has_contents fail' % (log_key))
            else:
                self.assertTrue(log.has_contents, 'Log %s has_contents fail' % (log_key))
        
        ief_dir = 'None'
        tcf_dir = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\GoS\\tuflow\\runs'
        self.assertEqual(ief_dir, all_logs.ief_dir, 'ief_dir fail')
        self.assertEqual(tcf_dir, all_logs.tcf_dir, 'tcf_dir fail')
        
    
    def getGosDict(self):
        
        GOS_DICT = {
            'BC_DBASE': [{'BC_DBASE': 'bc_dbase_grange_T100D5CC_CWI_MHWS.csv',
                          'COMMENTS': 'None',
                          'DATE': '27/03/2016',
                          'FILES': ['Pond.csv',
                                    'inflow.csv',
                                    'dsbdy.csv',
                                    'Spring.csv',
                                    'ds_pond.csv']}],
            'DAT': [{'AMENDMENTS': 'None',
                      'COMMENTS': 'None',
                      'DAT': 'None',
                      'DATE': '27/03/2016'}],
            'ECF': [{'COMMENTS': 'None',
                      'DATE': '27/03/2016',
                      'ECF': 'Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.ecf',
                      'FILES': ['bc_dbase_grange_T100D5CC_CWI_MHWS.csv',
                                '1d_bc_grange004_Option1aPlus.mif',
                                '1d_nwk_grange_Option1aPlus_ilo3_1-00.mif',
                                '1d_xs_grange005_Option1A_01.mif',
                                '1d_Wll_grange002.mif',
                                '1d_iwl_Option1a_1-00.mif']}],
            'RUN': [{'BC_DBASE': '[bc_dbase_grange_T100D5CC_CWI_MHWS.csv]',
                      'COMMENTS': 'None',
                      'DAT': 'None',
                      'DATE': '27/03/2016',
                      'DESCRIPTION': 'None',
                      'ECF': '[Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.ecf]',
                      'EVENT_DURATION': '20.0',
                      'EVENT_NAME': 'None',
                      'IEF': 'None',
                      'IEF_DIR': 'None',
                      'ISIS_BUILD': 'None',
                      'LOG_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\GoS\\tuflow\\runs\\..\\Runs\\Log\\Cul_free\\',
                      'MB': 'None',
                      'MODELLER': 'None',
                      'RESULTS_LOCATION_1D': 'None',
                      'RESULTS_LOCATION_2D': '..\\results\\2d\\Cul_free\\Option1aPlus\\',
                      'RUN_OPTIONS': 'None',
                      'RUN_STATUS': 'None',
                      'SETUP': 'None',
                      'TBC': '[Grange_baseline_Option1APlus_v1-00.tbc]',
                      'TCF': '[Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.tcf]',
                      'TCF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\GoS\\tuflow\\runs',
                      'TEF': 'None',
                      'TGC': '[Grange_baseline_Option1A_v1-00.tgc, Grange_baseline_Option1A_v1-00_test.tgc]',
                      'TUFLOW_BUILD': 'None'}],
            'TBC': [{'COMMENTS': 'None',
                      'DATE': '27/03/2016',
                      'FILES': ['2d_bc_hx_Option1aPlus_1-00.mif', '2d_bc_grange_option8.mif'],
                      'TBC': 'Grange_baseline_Option1APlus_v1-00.tbc'}],
            'TCF': [{'COMMENTS': 'None',
                      'DATE': '27/03/2016',
                      'FILES': ['Grange_baseline_Option1A_v1-00.tgc',
                                'Grange_baseline_Option1A_v1-00_test.tgc',
                                'grange001.tmf',
                                'Grange_baseline_Option1APlus_v1-00.tbc',
                                'bc_dbase_grange_T100D5CC_CWI_MHWS.csv',
                                'Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.ecf',
                                '2d_po_grange001.mif',
                                '2d_iwl_pond.mif'],
                      'TCF': 'Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.tcf'}],
            'TEF': [{'COMMENTS': 'None', 'DATE': '27/03/2016', 'FILES': 'None', 'TEF': 'None'}],
            'TGC': [{'COMMENTS': 'None',
                      'DATE': '27/03/2016',
                      'FILES': ['2d_loc_Grange001.mif',
                                '2d_code_grange001.mif',
                                '2d_bc_grange_option8.mif',
                                '2d_zpt_grange001.mid',
                                '2d_zln_grange_walls.mif',
                                '2d_zln_Option1a_cp_pond_reduction_v1-00.mif',
                                '2d_mat_grange002.mif'],
                      'TGC': 'Grange_baseline_Option1A_v1-00.tgc'},
                     {'COMMENTS': 'None',
                      'DATE': '27/03/2016',
                      'FILES': ['2d_loc_Grange001.mif',
                                '2d_code_grange001.mif',
                                '2d_bc_grange_option8.mif',
                                '2d_zpt_grange001.mid',
                                '2d_zln_grange_walls.mif',
                                '2d_zln_Option1a_cp_pond_reduction_v1-00.mif',
                                '2d_mat_grange002.mif'],
                      'TGC': 'Grange_baseline_Option1A_v1-00_test.tgc'}]
        }
        return GOS_DICT
        
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
                    'IEF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\iefs',
                    'ISIS_BUILD': 'None',
                    'LOG_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\Log\\',
                    'MB': 'None',
                    'MODELLER': 'None',
                    'RESULTS_LOCATION_1D': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18',
                    'RESULTS_LOCATION_2D': '..\\results\\2d\\kennford_1%AEP_FINAL_v5.18\\',
                    'RUN_OPTIONS': 'None',
                    'RUN_STATUS': 'None',
                    'SETUP': 'None',
                    'TBC': '[kennford_v3.5.tbc]',
                    'TCF': '[kennford_1%AEP_FINAL_v5.18.tcf]',
                    'TCF_DIR': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs',
                    'TEF': 'None',
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
            'TEF': [{'COMMENTS': 'None', 'DATE': '27/03/2016', 'FILES': 'None', 'TEF': 'None'}],
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
        