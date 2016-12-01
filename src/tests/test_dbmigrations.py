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
import dbmigrations as migrations
import globalsettings as gs
 
# Set to test model
gs.__TEST_MODE__ = True

# Need to call this here to avoid some weird behaviour
app = QApplication(sys.argv)
 
 
class ModelExtractorTest(unittest.TestCase):
     
    def setUp(self):
        """
        """
        settings = LogIT.LogitSettings()
        settings.cur_settings_path = os.path.join(os.getcwd(), 'settings.logset')
        self.form = LogIT.MainGui(LogIT.LogitSettings())
        self.versions = self.setupTestDatabases() 
    
    def tearDown(self):
        """
        """
        for v in self.versions:
            os.remove(v['file'])
            p = os.path.join(os.path.dirname(v['file']), os.path.basename(v['file']).replace('.logdb', 'backup.logdb'))
            try:
                os.remove(p)
            except:
                print ('\nNo backup to remove.\n' + str(p) + '\n')
    
    def test_geRequiredUpdates(self):
        for v in self.versions:
            updates = migrations.getRequiredUpdates(v['file'])
            if isinstance(updates, list):
                self.assertEqual(len(updates), v['updates'])
            else:
                self.assertEqual(updates, v['status'])
        
    def test_runUpdates(self):
        for v in self.versions:
            msg = self.form._updateDatabaseVersion(v['file'])
            self.assertEqual(msg, v['msg'])


    def setupTestDatabases(self):
        """
        """
        db_folder = r'C:\Users\duncan.runnacles\Documents\Programming\Python\Logit\Regression_Test_Data\Loader\databases\Database_versions'
        temp_folder = os.path.join(db_folder, '..', 'temp')

        versions = [
            {'name': 'NewDB_v20.logdb', 'updates': 1, 'msg': 'success'},
            {'name': 'NewDB_v21.logdb', 'updates': 0, 'msg': 'latest', 'status': 0} # status = DATABASE_VERSION_SAME
        ]
        for v in versions:
            v['file'] = os.path.join(temp_folder, v['name'])
            shutil.copyfile(os.path.join(db_folder, v['name']), v['file'])
        return versions
            

