import unittest
import sys
import os
import uuid
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import LogIT
from runsummary import RunSummary
# from runsummary.RunSummary import LogSummaryEntry

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)


class RunSummaryTest(unittest.TestCase):
    
    def setUp(self):
        """
        """
        self.form = LogIT.MainGui(False, os.path.join(os.getcwd(), 'settings.logset'))
        self.summary = self.form.widgets['Run Summary']
        self.data_dir = r'C:\Some\Fake\path'
        self.test_dir = r'C:\Users\duncan.runnacles\Documents\Programming\Python\LogITApp\Regression_Test_Data\Run_Summary'
        self.guid = '6941c7f2-4a7c-40fb-a2df-15c2f5ef224a'
    
    
    def test_getHoursFromDateStr(self):
        """
        """
        test_time1 = '3:15:00'
        test_time2 = '13:45:00'
        hours1, time = self.summary.getHoursFromDateStr(test_time1)
        hours2, time = self.summary.getHoursFromDateStr(test_time2)
        self.assertEqual(hours1, 3.25, 'hours1 equality test fail')
        self.assertEqual(hours2, 13.75, 'hours2 equality test fail')
    
    
    def test_loadLogContents(self):
        """
        """
        
        # Test completed run
        tlf_path = os.path.join(self.test_dir, 'test_complete.tlf')
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        entry = RunSummary.LogSummaryEntry(self.guid, run_name, self.data_dir, tlf_path) 
        entry, log_store = self.summary._loadLogContents(entry, tlf_path)
        
        COMPLETE_ROW_VALUES = {'COMPLETION': 0.25,
                               'GUID': '6941c7f2-4a7c-40fb-a2df-15c2f5ef224a',
                               'MAX_DDV': 0,
                               'MAX_MB': 4.2,
                               'NAME': 'test_complete',
                               'STATUS': 'Complete'}
        
        self.assertTrue(entry.finished, 'Completed finish status fail')
        self.assertFalse(entry.interrupted, 'Completed interrupted status fail')
        self.assertFalse(entry.error, 'Completed error status fail')
        self.assertTrue(entry.in_results, 'Completed in_results status fail')
        self.assertEqual(entry.cur_row, 935, 'Complete cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'Complete cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'Complete start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'Complete finish_time fail')
        self.assertDictEqual(entry.row_values, COMPLETE_ROW_VALUES, 'Complete row_values fail')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'Complete stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_complete.tlf', 'Complete tlf_path fail')
        self.assertEqual(len(log_store.ddv), 91, 'Complete ddv length fail')
        self.assertEqual(len(log_store.mb), 91, 'Complete mb length fail')
        self.assertEqual(len(log_store.flow_out), 91, 'Complete flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 91, 'Complete flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 91, 'Complete time_steps length fail')
        self.assertEqual(log_store.time_steps[-1], 0.25, 'Complete time_steps final value fail')
        self.assertEqual(log_store.start_time, 0.0, 'Complete log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'Complete log_store finish_time fail')

        
        # Test iterrupted run
        tlf_path = os.path.join(self.test_dir, 'test_interrupted.tlf')
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        entry = RunSummary.LogSummaryEntry(self.guid, run_name, self.data_dir, tlf_path) 
        entry, log_store = self.summary._loadLogContents(entry, tlf_path)
        
        INTERRUPTED_ROW_VALUES = {'COMPLETION': 0.08333333333333333,
                                  'GUID': '6941c7f2-4a7c-40fb-a2df-15c2f5ef224a',
                                  'MAX_DDV': 0,
                                  'MAX_MB': 4.2,
                                  'NAME': 'test_interrupted',
                                  'STATUS': 'Failed'}
        
        self.assertFalse(entry.finished, 'Interrupted finished status fail')
        self.assertTrue(entry.interrupted, 'Interrupted interrupted status fail')
        self.assertFalse(entry.error, 'Interrupted error status fail')
        self.assertTrue(entry.in_results, 'Interrupted in_results status fail')
        self.assertEqual(entry.cur_row, 360, 'Interrupted cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'Interrupted cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'Interrupted start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'Interrupted finish_time fail')
        self.assertDictEqual(entry.row_values, INTERRUPTED_ROW_VALUES, 'Interrupted row_values fail')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'Interrupted stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_interrupted.tlf', 'Interrupted tlf_path fail')
        self.assertEqual(len(log_store.ddv), 33, 'Interrupted ddv length fail')
        self.assertEqual(len(log_store.mb), 33, 'Interrupted mb length fail')
        self.assertEqual(len(log_store.flow_out), 33, 'Interrupted flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 33, 'Interrupted flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 33, 'Interrupted time_steps length fail')
        self.assertAlmostEqual(log_store.time_steps[-1], 0.08333333333333333, 'Interrupted time_steps final value fail')
        self.assertEqual(log_store.start_time, 0.0, 'Interrupted log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'Interrupted log_store finish_time fail')
        
         # Test unstable run
        tlf_path = os.path.join(self.test_dir, 'test_unstable.tlf')
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        entry = RunSummary.LogSummaryEntry(self.guid, run_name, self.data_dir, tlf_path) 
        entry, log_store = self.summary._loadLogContents(entry, tlf_path)
        
        UNSTABLE_ROW_VALUES = {'COMPLETION': 0.08333333333333333,
                               'GUID': '6941c7f2-4a7c-40fb-a2df-15c2f5ef224a',
                               'MAX_DDV': 0,
                               'MAX_MB': 4.2,
                               'NAME': 'test_unstable',
                               'STATUS': 'Failed'}
        
        self.assertFalse(entry.finished, 'Unstable finished status fail')
        self.assertFalse(entry.interrupted, 'Unstable interrupted status fail')
        self.assertTrue(entry.error, 'Unstable error status fail')
        self.assertTrue(entry.in_results, 'Unstable in_results status fail')
        self.assertEqual(entry.cur_row, 360, 'Unstable cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'Unstable cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'Unstable start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'Unstable finish_time fail')
        self.assertDictEqual(entry.row_values, UNSTABLE_ROW_VALUES, 'Unstable row_values fail')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'Unstable stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_unstable.tlf', 'Unstable tlf_path fail')
        self.assertEqual(len(log_store.ddv), 33, 'Unstable ddv length fail')
        self.assertEqual(len(log_store.mb), 33, 'Unstable mb length fail')
        self.assertEqual(len(log_store.flow_out), 33, 'Unstable flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 33, 'Unstable flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 33, 'Unstable time_steps length fail')
        self.assertAlmostEqual(log_store.time_steps[-1], 0.08333333333333333, 'Unstable time_steps final value fail')
        self.assertEqual(log_store.start_time, 0.0, 'Unstable log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'Unstable log_store finish_time fail')
        
        
        # Test partial run followed by completed run
        tlf_path = os.path.join(self.test_dir, 'test_partial.tlf')
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        entry = RunSummary.LogSummaryEntry(self.guid, run_name, self.data_dir, tlf_path) 
        entry, log_store = self.summary._loadLogContents(entry, tlf_path)
        
        self.assertFalse(entry.finished, 'Partial finished status fail')
        self.assertFalse(entry.interrupted, 'Partial interrupted status fail')
        self.assertFalse(entry.error, 'Partial error status fail')
        self.assertTrue(entry.in_results, 'Partial in_results status fail')
        self.assertEqual(entry.cur_row, 357, 'Partial cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'Partial cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'Partial start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'Partial finish_time fail')
        self.assertEqual(entry.row_values['MAX_DDV'], 0, 'partial row_values ddv fail')
        self.assertAlmostEqual(entry.row_values['COMPLETION'], 0.08333333333333333, 'partial row_values completion fail')
        self.assertEqual(entry.row_values['MAX_MB'], 4.2, 'partial row_values MB fail')
        self.assertEqual(entry.row_values['NAME'], 'test_partial', 'partial row_values name fail')
        self.assertEqual(entry.row_values['STATUS'], 'In Progress', 'partial row_values status fail')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'Partial stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_partial.tlf', 'Partial tlf_path fail')
        self.assertEqual(len(log_store.ddv), 33, 'Partial ddv length fail')
        self.assertEqual(len(log_store.mb), 33, 'Partial mb length fail')
        self.assertEqual(len(log_store.flow_out), 33, 'Partial flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 33, 'Partial flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 33, 'Partial time_steps length fail')
        self.assertAlmostEqual(log_store.time_steps[-1], 0.08333333333333333, 'Partial time_steps final value fail')
        self.assertEqual(log_store.start_time, 0.0, 'Partial log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'Partial log_store finish_time fail')
        
        tlf_path = os.path.join(self.test_dir, 'test_complete.tlf')
        entry.row_values['NAME'] = 'test_complete'
        entry.tlf_path = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_complete.tlf'
        entry, log_store = self.summary._loadLogContents(entry, tlf_path, log_store)
        
        COMPLETE_ROW_VALUES = {'COMPLETION': 0.25,
                               'GUID': '6941c7f2-4a7c-40fb-a2df-15c2f5ef224a',
                               'MAX_DDV': 0,
                               'MAX_MB': 4.2,
                               'NAME': 'test_complete',
                               'STATUS': 'Complete'}
        
        # These completed run values should be the same as if it was run all 
        # the way through initally. i.e. should be the same as the first 
        # completed run test
        self.assertTrue(entry.finished, 'Complete after partial finished status fail')
        self.assertFalse(entry.interrupted, 'Complete after partial interrupted status fail')
        self.assertFalse(entry.error, 'Complete after partial error status fail')
        self.assertTrue(entry.in_results, 'Complete after partial in_results status fail')
        self.assertEqual(entry.cur_row, 935, 'Complete after partial cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'Complete after partial cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'Complete after partial start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'Complete after partial finish_time fail')
        self.assertDictEqual(entry.row_values, COMPLETE_ROW_VALUES, 'Complete after partial row_values fa.il')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'Complete after partial stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_complete.tlf', 'Complete after partial tlf_path fail')
        self.assertEqual(len(log_store.ddv), 91, 'Complete after partial ddv length fail')
        self.assertEqual(len(log_store.mb), 91, 'Complete after partial mb length fail')
        self.assertEqual(len(log_store.flow_out), 91, 'Complete after partial flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 91, 'Complete after partial flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 91, 'Complete after partial time_steps length fail')
        self.assertEqual(log_store.time_steps[-1], 0.25, 'Complete after partial time_steps final value fail')
        self.assertEqual(log_store.start_time, 0.0, 'Complete after partial log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'Complete after partial log_store finish_time fail')
        
        
        # Test Run that hasn't reached results section yet
        tlf_path = os.path.join(self.test_dir, 'test_noresults.tlf')
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        entry = RunSummary.LogSummaryEntry(self.guid, run_name, self.data_dir, tlf_path) 
        entry, log_store = self.summary._loadLogContents(entry, tlf_path)
        
        self.assertFalse(entry.finished, 'No results finished status fail')
        self.assertFalse(entry.interrupted, 'No results interrupted status fail')
        self.assertFalse(entry.error, 'No results error status fail')
        self.assertFalse(entry.in_results, 'No results in_results status fail')
        self.assertEqual(entry.cur_row, 21, 'No results cur_row fail')
        self.assertEqual(entry.cur_time, 0, 'No results cur_time fail')
        self.assertEqual(entry.start_time, 0.0, 'No results start_time fail')
        self.assertEqual(entry.finish_time, 0.25, 'No results finish_time fail')
        self.assertEqual(entry.row_values['MAX_DDV'], 0, 'partial row_values ddv fail')
        self.assertAlmostEqual(entry.row_values['COMPLETION'], 0, 'partial row_values completion fail')
        self.assertEqual(entry.row_values['MAX_MB'], 0, 'partial row_values MB fail')
        self.assertEqual(entry.row_values['NAME'], 'test_noresults', 'partial row_values name fail')
        self.assertEqual(entry.row_values['STATUS'], 'In Progress', 'partial row_values status fail')
        self.assertEqual(entry.stored_datapath, 'C:\\Some\\Fake\\path\\6941c7f2-4a7c-40fb-a2df-15c2f5ef224a.dat', 'No results stored_datapth fail')
        self.assertEqual(entry.tlf_path, 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\LogITApp\\Regression_Test_Data\\Run_Summary\\test_noresults.tlf', 'No results tlf_path fail')
        self.assertEqual(len(log_store.ddv), 0, 'No results ddv length fail')
        self.assertEqual(len(log_store.mb), 0, 'No results mb length fail')
        self.assertEqual(len(log_store.flow_out), 0, 'No results flow_in length fail')
        self.assertEqual(len(log_store.flow_in), 0, 'No results flow_out length fail')
        self.assertEqual(len(log_store.time_steps), 0, 'No results time_steps length fail')
        self.assertEqual(log_store.start_time, 0.0, 'No results log_store start_time fail')
        self.assertEqual(log_store.finish_time, 0.25, 'No results log_store finish_time fail')

        
        i=0
#         self.form.settings.log_summarys.append(entry)






