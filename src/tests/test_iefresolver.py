import unittest
import sys
import os
import shutil
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
 
import LogIT
import IefResolver
from IefResolver import IefHolder
 
from ship.utils.fileloaders import fileloader as fl
 
# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)
 
 
class IefResolverTest(unittest.TestCase):
     
    def setUp(self):
        """
        """
        settings = LogIT.LogitSettings()
        settings.cur_settings_path = os.path.join(os.getcwd(), 'settings.logset')
        self.form = LogIT.MainGui(LogIT.LogitSettings())
 
     
    def test_autoResolvePath(self):
        """
        """
        ief_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Ief_Resolver\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        success, ief_holder = IefResolver.autoResolvePath(ief_path)
        self.assertTrue(success, 'Ief resolve true fail')
         
        self.assertTrue(ief_holder.has_types['.tcf'], 'Has types tcf fail')
        self.assertTrue(ief_holder.has_types['result'], 'Has types result fail')
        self.assertTrue(ief_holder.has_types['.dat'], 'Has types dat fail')
        self.assertFalse(ief_holder.has_types['.ied'], 'Has types ied fail')
        self.assertFalse(ief_holder.missing_types['.tcf'], 'Missing types tcf fail')
        self.assertFalse(ief_holder.missing_types['result'], 'Missing types result fail')
        self.assertFalse(ief_holder.missing_types['.dat'], 'Missing types dat fail')
        self.assertTrue(ief_holder.missing_types['.ied'], 'Missing types ied fail')
         
        root_new = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\'
        root_old = 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\'
        self.assertEqual(ief_holder.root_folder_new, root_new, 'Root new fail')
        self.assertEqual(ief_holder.root_folder_old, root_old, 'Root old fail')
         
        single_types = {'.dat': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT',
                                 'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT'},
                        '.tcf': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf',
                                 'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'},
                        'result': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.18',
                                   'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.18'}}
        self.assertDictEqual(ief_holder.single_types, single_types, 'Single types fail')
         
        self.assertEqual(ief_holder.result_name, 'KENNFORD_1%AEP_FINAL_V5.18', 'Result name fail')
     
     
    def test_resolveUnfoundPaths(self):
        """
        """
        ief_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Ief_Resolver\model\isis\iefs\kennford_1%AEP_FINAL_v5.20.ief'
        loader = fl.FileLoader()
        ief = loader.loadFile(ief_path)
        holders = [self.getUnsolvedIefHolder(ief)]
        holders, had_to_search = IefResolver.resolveUnfoundPaths(holders)
        holder = holders[0]
         
        test_hadtosearch = {'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\iefs\\kennford_1%AEP_FINAL_v5.20.ief': 
                            {'in': ['P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.19\\KENNFORD_1%AEP_FINAL_V5.19'],
                             'out': ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\trick_file_location\\kennford_1%AEP_FINAL_v5.19\\KENNFORD_1%AEP_FINAL_V5.19']
                            }
                           }
        test_missingtypes = {'.tcf': False, '.ied': True, 'result': False, '.dat': False}
        test_singletypes = {'.dat': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT',
                                     'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT'},
                            '.tcf': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf',
                                     'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'},
                            'result': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.19',
                                       'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\trick_file_location\\kennford_1%AEP_FINAL_v5.19'}}
         
        self.assertDictEqual(test_hadtosearch, had_to_search,'had_to_search equality fail')
        self.assertDictEqual(test_missingtypes, holder.missing_types, 'missing_types equality fail')
        self.assertDictEqual(test_singletypes, holder.single_types, 'single_types equality fail')
         
        i=0
         
     
    def test_updateIedObjects(self):
        """
        """
        ief_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Ief_Resolver\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        success, ief_holder = IefResolver.autoResolvePath(ief_path)
        self.assertTrue(success, 'Ief resolve true fail')
         
        iefs = IefResolver.updateIefObjects([ief_holder])
        self.assertEqual(len(iefs), 1, 'Ief list length fail')
         
        ief = iefs[0]
        twod = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'
        dat = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT'
        result = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.18\\KENNFORD_1%AEP_FINAL_V5.18'
        self.assertEqual(ief.event_details['2DFile'], twod, 'Update 2DFile fail')
        self.assertEqual(ief.event_header['Datafile'], dat, 'Update Datafile fail')
        self.assertEqual(ief.event_header['Results'], result, 'Update Result fail')
         
     
    def test_findFile(self):
        """
        """
        ief_dir = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Ief_Resolver\model\isis\iefs'
        find_file = 'kennford_1%AEP_FINAL_v5.18.tcf'
        find_file_false = 'kennford_1%AEP_FINAL_v5.19.tcf'
        result = ['C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\trick_file_location\\kennford_1%AEP_FINAL_v5.18.tcf',
                  'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf',
                  'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Loader\\model\\Kennford\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'
                 ]
        temp = IefResolver.findFile(ief_dir, find_file, 4)
        self.assertEqual(IefResolver.findFile(ief_dir, find_file, 4), result, 'Find file true fail')
        self.assertFalse(IefResolver.findFile(ief_dir, find_file_false), 'Find file false fail')
     
     
    def test_longestCommonPrefix(self):
        """
        """
        f1 = r'C:\Folder\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        f2 = r'C:\Folder\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        f3 = r'C:\A\different\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        f4 = r'S:\A\different\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        result = 'C:\\Folder\\model\\'
         
        temp = IefResolver.longestCommonPrefix(f1, f2)
        self.assertEqual(IefResolver.longestCommonPrefix(f1, f2), result, 'Prefix test fail')
        self.assertEqual(IefResolver.longestCommonPrefix(f2, f3), 'C:\\', 'Prefix no result test fail')
        self.assertEqual(IefResolver.longestCommonPrefix(f2, f4), '', 'Prefix no result test fail')
     
     
    def test_longestCommonSuffix(self):
        """
        """
        f1 = r'C:\Folder\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
        f2 = r'C:\Folder\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        f3 = r'C:\A\different\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        f4 = r'S:\A\different\model\tuflow\runs\kennford_1%AEP_FINAL_v5.18.tcf'
        result1 = ':\\A\\different\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'
        result2= '\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'
         
        self.assertEqual(IefResolver.longestCommonSuffix(f3, f4), result1, 'Suffix test fail')
        self.assertEqual(IefResolver.longestCommonSuffix(f2, f3), result2, 'Suffix test fail')
        self.assertEqual(IefResolver.longestCommonSuffix(f1, f2), 'f', 'Suffix no result test fail')
         
         
    def getUnsolvedIefHolder(self, ief):
        """
        """
        holder = IefHolder(ief)
        holder.has_types = {'.dat': True, '.ied': False, '.tcf': True, 'result': True}
        holder.missing_types = {'.dat': False, '.ied': True, '.tcf': False, 'result': True}
        holder.result_name = 'KENNFORD_1%AEP_FINAL_V5.19'
        holder.root_folder_new = 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\'
        holder.root_folder_old = 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\'
        holder.selected_paths = {'.dat': '', '.ied': '', '.tcf': '', 'result': ''}
        holder.single_types = {'.dat': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT',
                                        'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\isis\\dat\\kennford_1%AEP_FINAL_v1.17\\kennford_1%AEP_FINAL_v1.17.DAT'},
                               '.tcf': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf',
                                        'out': 'C:\\Users\\duncan.runnacles\\Documents\\Programming\\Python\\Logit\\Regression_Test_Data\\Ief_Resolver\\model\\tuflow\\runs\\kennford_1%AEP_FINAL_v5.18.tcf'},
                               'result': {'in': 'P:\\00 Project Files\\13059 EA SW Consultancy Support\\Technical\\Kennford_model\\model\\hydraulics\\Final_Model\\model\\isis\\results\\kennford_1%AEP_FINAL_v5.19',
                                          'out': ''}}
        return holder
         
         
         
         