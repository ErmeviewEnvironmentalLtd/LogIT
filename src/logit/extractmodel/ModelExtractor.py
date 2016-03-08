"""
###############################################################################
    
 Name: LogIT (Logger for Isis and Tuflow) 
 Author: Duncan Runnacles
 Copyright: (C) 2014 Duncan Runnacles
 email: duncan.runnacles@thomasmackay.co.uk
 License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


 Module:          ModelExtractor.py 
 Date:            04/03/2016
 Author:          Duncan Runnacles
 Since-Version:   0.4
 
 Summary:
    Copies the model at the path location stored in the log to a new directory.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import os
import time
import shutil

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from tmac_tools_lib.utils.filetools import MyFileDialogs
from tmac_tools_lib.utils.fileloaders.fileloader import FileLoader
from tmac_tools_lib.tuflow.tuflowfilepart import SomeFile
from tmac_tools_lib.tuflow.data_files import datafileloader
from tmac_tools_lib.utils import filetools
    
import  ModelExtractor_Widget as extractwidget



class ExtractVars(object):
    """Variable store more values used when extracting a model."""
    
    def __init__(self):
        self.tuflow = None
        self.ief = None
        self.tcf_path = None
        self.ief_path = None
        self.out_dir = None
        self.has_tcf = False
        
        self.in_files = []
        self.out_files = []
        self.results_files = []
        
        self.missing_model_files = []
        self.missing_results_files = []
        self.failed_data_files = []



class ModelExtractor_UI(QtGui.QWidget, extractwidget.Ui_ExtractModelWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)
        
        self.tool_name = 'Model Extractor'
        self.settings = ToolSettings()
        self.settings.cur_location = cwd
        
        self.setupUi(self)
        
        # Connect the slots
        self.extractModelFileButton.clicked.connect(self._setInputFile)
        self.extractOutputButton.clicked.connect(self._setOutputDirectory)
        self.extractModelButton.clicked.connect(self._extractModel)
    

    def _setInputFile(self):
        """Get the input model file to use."""

        if not self.settings.cur_model_path == '':
            path = self.settings.cur_model_path
        else:
            path = self.settings.cur_location

        d = MyFileDialogs()
        open_path = d.openFileDialog(path, file_types='Ief/Tcf File(*.ief;*tcf)')
        if open_path == 'False' or open_path == False:
            return
        
        self.extractModelFileTextbox.setText(open_path)
        self.settings.cur_model_path = open_path         
        
    
    def _setOutputDirectory(self):
        """Set the directory to extract the model to."""

        if not self.settings.cur_model_path == '':
            path = self.settings.cur_output_dir
        else:
            path = self.settings.cur_location

        d = MyFileDialogs()
        dir_path = d.dirFileDialog(path) 
        if dir_path == 'False' or dir_path == False:
            return
        
        self.extractOutputTextbox.setText(dir_path)
        self.settings.cur_output_dir = dir_path
        
    
    def _extractModel(self):
        """
        """
        self._extractVars = ExtractVars()
        self.extractOutputTextArea.clear()
        
        in_path = str(self.extractModelFileTextbox.text())
        out_dir = str(self.extractOutputTextbox.text())
         
        if not os.path.exists(in_path):
            logger.error('Model file does not exist')
            QtGui.QMessageBox.warning(self, "File not found",
                                      "Model file does not exist")
        if not os.path.exists(out_dir):
            logger.error('Output directory does not exist')
            QtGui.QMessageBox.warning(self, "Directory not found",
                                      "Output directory does not exist")

        self._extractVars.out_dir = out_dir
        
        # Check if we're dealing with an ief or a tcf
        ext = os.path.splitext(in_path)[1]
        if ext == '.ief':
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Reading ISIS/FMP files')
            self._extractVars.ief_path = in_path
            self._getIsisFiles()
        else:
            if not ext == '.tcf':
                logger.error('File type is not recognised:\n' + in_path)
            self._extractVars.tcf_path = in_path
            self.has_tcf = True
            
        if not self._extractVars.tcf_path == None:
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Reading Tuflow files')
            self._extractVars.out_dir = os.path.join(self._extractVars.out_dir, 'tuflow','runs')
            loader = FileLoader()
            self._extractVars.tuflow = loader.loadFile(self._extractVars.tcf_path)
            self._loadModelFiles()
            
            success = self._updateModelFilePaths() 
            if not success:
                return

            tuflow_files = self._extractVars.tuflow.getPrintableContents()
        
        elif not self._extractVars.has_tcf:
            logger.error('Model has found tcf but tcf_path is None')
            return 
            
        
        # Get the input and output files together and copy everything
        combo_files = self._mergeFiles() 
        self._writeOutResultsFiles() 
        self._writeOutModelFiles(combo_files)
        
        if not self._extractVars.ief == None:
            contents = self._extractVars.ief.getPrintableContents()
            p = self._extractVars.ief.path_holder.getAbsPath()
            d = os.path.split(p)[0]
            if not os.path.exists(d):
                os.makedirs(d, 0777)
            filetools.writeFile(contents, 
                                self._extractVars.ief.path_holder.getAbsPath(), 
                                add_newline=True)
        
        if not self._extractVars.tcf_path == None:
            for path, contents in tuflow_files.iteritems():
                filetools.writeFile(contents, path, add_newline=False)
        
        self._displayOutput()
        
        self.emit(QtCore.SIGNAL("updateProgress"), 0)
        self.emit(QtCore.SIGNAL("statusUpdate"), '')
    
    
    def _displayOutput(self):
        """
        """
        output = []
        output.append('\n Model extraction complete.')
        
        if self._extractVars.failed_data_files:
            output.append('\n\nUnable to load some datafiles - These may contain references to other files which have not been found.')
            output.append('The following files could not be loaded:\n')
            for d in self._extractVars.failed_data_files:
                output.append(d) 

        if self._extractVars.missing_model_files:
            output.append('\n\nCould not copy some model files - check that they exist.')
            output.append('The following files could not be copied:\n')
            for m in self._extractVars.missing_model_files:
                output.append(m) 
        
        if self._extractVars.missing_results_files:
            output.append('\n\nCould not copy some results files - check that they exist.')
            output.append('The following files could not be copied:\n')
            for r in self._extractVars.missing_results_files:
                output.append(r) 
                
        output = '\n'.join(output)
        self.extractOutputTextArea.setText(output)
                
    
    def _writeOutModelFiles(self, file_paths):
        """Write out the model to the new directory.
        
        Loop through all of the paths that we grabbed copying them from the
        original file paths into the new one. If the directories that we are
        copying to don't exist we make them. If there is an error finding the
        file to copy or it can't be saved to the new list make a record of it
        to display to the user.
        """
        
        curd = os.getcwd()
        not_moved = []
        no_results = len(file_paths)

        self.emit(QtCore.SIGNAL("statusUpdate"), 'Copying model files...')
        self.emit(QtCore.SIGNAL("setRange"), no_results)
        for i, p in enumerate(file_paths, 1):
            tester = os.path.exists(p[0])
            if os.path.exists(p[0]):

                try:
                    d = os.path.dirname(p[1])
                    if not os.path.exists(d):
                        os.makedirs(d, 0777)
                except IOError:
                    print 'Cannot make directory for: ' + p[1]
                    continue

                try:
                    if not os.path.isdir(p[0]):
                        d, f = os.path.split(p[0])
                        os.chdir(d)
                        self.emit(QtCore.SIGNAL("updateProgress"), i)
                        shutil.copy(f, p[1])
                except IOError:
                    self._extractVars.missing_model_files.append(p[0])

            else:
                self._extractVars.missing_model_files.append(p[0])

        os.chdir(curd)
    
    
    def _writeOutResultsFiles(self): 
        """Copy the result files into the new directory.
        """
        curd = os.getcwd()
        results_names_in = []
        results_names_out = []
        
        no_results_folders = len(self._extractVars.results_files)
        for i, r in enumerate(self._extractVars.results_files, 1):
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Copying output folder %s of %s' % (i, no_results_folders))
            old_p, old_n = os.path.split(r[0])
            new_p, new_n = os.path.split(r[1])
            
            if not os.path.exists(old_p):
                logger.warning('Could not copy results from: ' + old_p)
                continue
            
            file_list = os.listdir(old_p)
            
            try:
                if os.path.isdir(new_p):
                    d = os.path.dirname(new_p)
                else:
                    d = new_p

                if not os.path.exists(d):
                    os.makedirs(d, 0777)
            except IOError:
                print 'Cannot make directory for: ' + new_p
                continue
            
            # Need to do this in case we have some really long names
            os.chdir(old_p)
            
            no_results = len(file_list)
            self.emit(QtCore.SIGNAL("setRange"), no_results)
            found_file = False
            
            '''Results are always several files with the same name, but
               different extensions. This checks that the filename + extension
               starts with the same string.
            '''
            for j, f in enumerate(file_list, 1):
                if f.startswith(old_n):
                    found_file = True
                    try:
                        self.emit(QtCore.SIGNAL("updateProgress"), j)
                        shutil.copy(f, new_p)
                    except IOError:
                        self._extractVars.missing_results_files.append(r[0])
            
            if not found_file:
                self._extractVars.missing_results_files.append(r[0])
        
        os.chdir(curd)

    
    def _fetchResultsFiles(self, model_file, rel_root, model_root, run_name): 
        """Fetches the output files from the tuflow model.
        
        Args:
            model_file(ATuflowModelFile): the model file being read.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
            run_name(str): the name of the tuflow entry file (tcf/ecf).
        
        These are the result, check and log files.
        """
        result_hashes = model_file.getHashCategory(self._extractVars.tuflow.RESULT)
        for r in result_hashes:
            part = self._extractVars.tuflow.file_parts[r]
            
            if part.command.upper() == 'OUTPUT FOLDER':
                if model_file.TYPE == 'tcf':
                    new_root = r'..\results\2d'
                else:
                    new_root = r'..\results\1d'
            
            elif part.command.upper() == 'WRITE CHECK FILES':
                new_root = r'..\checks'

            if part.file_name == '':
                p = os.path.join(part.root, part.parent_relative_root, part.relative_root)
                self._extractVars.results_files.append([os.path.join(p, run_name),
                                          os.path.join(self._extractVars.out_dir, new_root, run_name)
                                         ])
            else:
                self._extractVars.results_files.append([os.path.join(p, part.file_name),
                                          os.path.join(self._extractVars.out_dir, new_root, part.file_name)
                                         ])

            part.relative_root = new_root
            part.parent_relative_root = rel_root
            self._extractVars.tuflow.file_parts[part.hex_hash] = part
        

    def _fetchDataFiles(self, model_file, source_root, rel_root, model_root): 
        """Get all of the data files and any subfiles they contain.
        
        Attempts to load any data files (.tmf, .csv, etc) and checks to see if
        they contain references to any subfiles. If they do it calls 
        getSourceFiles() to create the in and out paths for them as well.
        
        Args:
            model_file(ATuflowModelFile): the model file being read.
            source_root(str): location to set for the out file.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
        
        """
        data_hashes = model_file.getHashCategory(self._extractVars.tuflow.DATA)
        for d in data_hashes:
            part = self._extractVars.tuflow.file_parts[d]
            self._extractVars.in_files.extend(part.getAbsPath(all_types=True))
            
            data_subfiles = []
            if not part.extension == 'tmf':
                
                success = self._getSourceFiles(part, r'..\bc_dbase', model_root, rel_root)
                if not success:
                    self._extractVars.failed_data_files.append(part.getAbsPath()) 

            part.parent_relative_root = rel_root
            part.root = self._extractVars.out_dir
            
            if part.command.upper() == 'BC DATABASE':
                part.relative_root = os.path.join(model_root, source_root)
            
            elif part.command.upper() == 'READ MATERIALS FILE':
                part.relative_root = model_root
            
            self._extractVars.tuflow.file_parts[part.hex_hash] = part
            self._extractVars.out_files.extend(part.getAbsPath(all_types=True))


    def _getSourceFiles(self, data_file, source_root, model_root, rel_root): 
        """Get all of the sub files contained by a data file.
        
        Loads the given SomeFile reference and checks to see if it contains
        any references to other files. If it does it gets/sets the in/out file
        locations.
        
        Args:
            data_file(SomeFile): the ATuflowFilePart.
            source_root(str): location to set for the out file.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
        """
        missing_files = []
        try:
            dobj = datafileloader.loadDataFile(data_file)

            try:
                i = dobj.keys.SOURCE
            except AttributeError:
                return False 
            
            source = dobj.row_collection.getRowDataAsList(dobj.keys.SOURCE)
            for s in source:
                # Create a path holder
                f = filetools.PathHolder(s, data_file.root)
                f.relative_root = data_file.relative_root
                self._extractVars.in_files.append(f.getAbsPath())
                
                f.relative_root = os.path.join(model_root, source_root)
                f.parent_relative_root = rel_root
                f.root = self._extractVars.out_dir
                self._extractVars.out_files.append(f.getAbsPath())
                
        except IOError:
            return False 
        
        return True 


    def _fetchGisFiles(self, model_file, source_root, main_root, rel_root, model_root): 
        """Get all of the data files and any subfiles they contain.
        
        Attempts to load any data files (.tmf, .csv, etc) and checks to see if
        they contain references to any subfiles. If they do it calls 
        getSourceFiles() to create the in and out paths for them as well.
        
        Args:
            model_file(ATuflowModelFile): the model file being read.
            source_root(str): location to set for the out file.
            main_root(str): location to set for the gis file, which may be 
                different to that for the subfiles.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
        
        """
        hashes = model_file.getHashCategory(self._extractVars.tuflow.GIS)
        for h in hashes:
            part = self._extractVars.tuflow.file_parts[h]
            self._extractVars.in_files.extend(part.getAbsPath(all_types=True))
            
            if part.command.upper() == 'READ MI TABLE LINKS':
                
                success = self._getSourceFiles(part, 'xs', model_root, rel_root)
                if not success:
                    self._extractVars.failed_data_files.append(part.getAbsPath()) 

                part.relative_root = os.path.join(model_root, source_root)

            else:
                part.relative_root = os.path.join(model_root, main_root)
                
            part.parent_relative_root = rel_root

            part.root = self._extractVars.out_dir
            self._extractVars.tuflow.file_parts[part.hex_hash] = part
            self._extractVars.out_files.extend(part.getAbsPath(all_types=True))

    
    def _updateModelFilePaths(self): 
        """Update the paths of the ATuflowModelFiles (tcf, tgc, etc).
        
        These are being read and updated for the new location so it is
        important that they don't overwrite the existing versions. The paths
        before update are checked against those after update to ensure that 
        this can't happen. If there's an issue we stop and retreat.
        """
        out_name_check = []
        in_name_check = []
        
        models = self._extractVars.tuflow.getModelFiles()
        tcfs = self._extractVars.tuflow.getModelFiles('tcf')
        ecfs = self._extractVars.tuflow.getModelFiles('ecf')
        tbcs = self._extractVars.tuflow.getModelFiles('tbc')
        tgcs = self._extractVars.tuflow.getModelFiles('tgc')
        models = tcfs + ecfs + tbcs + tgcs
        
        try:
            for m in models:
                in_name_check.append(self._extractVars.tuflow.file_parts[m.hex_hash].root)
                m.parent_relative_root = r''
                m.root = self._extractVars.out_dir
                self._extractVars.tuflow.file_parts[m.hex_hash] = m
                out_name_check.append(self._extractVars.tuflow.file_parts[m.hex_hash].root) 
        except:
            logger.error('Problem changing paths - aborting to avoid overwriting file!')
            return False
        
        # Make sure all paths have been updated.
        for o in out_name_check:
            if o in in_name_check:
                logger.warning('Some file paths have failed to update - Aborting to avoid overwriting file!')
                return False
        
        return True
        
    
    def _mergeFiles(self): 
        """Combine the infile and outfiles lists.
        
        Take the in files list and the outfiles list and combine them, while
        removing any duplicate entries. 
        """
        no_dup_old = []
        for f in self._extractVars.in_files:
            if not f in no_dup_old: no_dup_old.append(f)
        
        no_dup_new = []
        for f in self._extractVars.out_files:
            if not f in no_dup_new: no_dup_new.append(f)
        
        combo = zip(no_dup_old, no_dup_new)
        return combo
        
        
    def _loadModelFiles(self): 
        """Gets copies of all of the model files and fetches their contents.
        
        Loops through all of the model files and fetches anything that can
        contain a files (gis files, data files, results files, etc). The 
        functions called updated the path variables on all of these files.
        """
        
        # Get only the path name of the main file.
        run_name = self._extractVars.tuflow.getModelFiles('main', name_only=True)[0]
        
        # Get the ATuflowModelFile reference of all of the others.
        tcfs = self._extractVars.tuflow.getModelFiles('tcf', tuflowmodelfile=True)
        ecfs = self._extractVars.tuflow.getModelFiles('ecf', tuflowmodelfile=True)
        tbcs = self._extractVars.tuflow.getModelFiles('tbc', tuflowmodelfile=True)
        tgcs = self._extractVars.tuflow.getModelFiles('tgc', tuflowmodelfile=True)
        model_files = tcfs + ecfs + tbcs + tgcs

        for m in model_files:
            category = m.TYPE
            if category == 'tcf' or category == 'ecf':
                model_root = r'..\model'
                rel_root = r''
            else:
                model_root = r''
                rel_root = r'..\model'
            
            self._fetchGisFiles(m, 'xs', 'gis', rel_root, model_root)

            self._fetchDataFiles(m, r'..\bc_dbase', rel_root, model_root)
            
            self._fetchResultsFiles(m, rel_root, model_root, run_name)
            
    
    def _getIsisFiles(self): 
        """Get all of the ISIS/FMP related files from the ief.
        
        Any reference to any file components in the ief is stored.
        """
        dat_name = ''
        
        loader = FileLoader()
        self._extractVars.ief = loader.loadFile(self._extractVars.ief_path)
        
        if '2DFile' in self._extractVars.ief.event_details.keys():
            self._extractVars.tcf_path = self._extractVars.ief.event_details['2DFile']
            out_tcf = os.path.split(self._extractVars.tcf_path)[1]
            self._extractVars.ief.event_details['2DFile'] = os.path.join(r'..\..\tuflow\runs', out_tcf)
            self._extractVars.has_tcf = True
        
        if 'InitialConditions' in self._extractVars.ief.event_details.keys():
            ic = self._extractVars.ief.event_details['InitialConditions']
            out_ic = os.path.join(os.path.split(ic)[1])
            self._extractVars.ief.event_details['InitialConditions'] = os.path.join(r'..\ics', out_ic)
            self._extractVars.in_files.append(ic)
            self._extractVars.out_files.append(os.path.join(self._extractVars.out_dir, r'fmp\ics', out_ic))

        if not self._extractVars.ief.event_header['Datafile'] == '':
            dat = self._extractVars.ief.event_header['Datafile']
            dat_name = os.path.splitext(os.path.split(dat)[1])[0]
            out_dat = os.path.join(self._extractVars.out_dir, r'fmp\dats', os.path.split(dat)[1])
            self._extractVars.ief.event_header['Datafile'] = os.path.join(r'..\dats', dat_name + '.dat')
            self._extractVars.in_files.append(dat)
            self._extractVars.out_files.append(out_dat)
            
        
        if not self._extractVars.ief.event_header['Results'] == '':
            d, f = os.path.split(self._extractVars.ief.event_header['Results'])
            self._extractVars.results_files.append([os.path.join(d, f),
                               os.path.join(self._extractVars.out_dir, r'fmp\results', f)
                              ])
            self._extractVars.ief.event_header['Results'] = r'..\results'
        
        for i, ied in enumerate(self._extractVars.ief.ied_data):
            ied_in = ied['file']
            ied_name = os.path.split(ied_in)[1]
            self._extractVars.ief.ied_data[i]['file'] = os.path.join(r'..\ieds', ied_name)
            self._extractVars.in_files.append(ied_in)
            self._extractVars.out_files.append(os.path.join(self._extractVars.out_dir, r'fmp\ieds', ied_name))
        

        self._extractVars.ief.path_holder.root = os.path.join(self._extractVars.out_dir, 'fmp', 'iefs')


    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        # Check that this version of the settings has all the necessary
        # attributes, and if not add the missing ones
        temp_set = ToolSettings()
        settings_attrs = [s for s in dir(temp_set) if not s.startswith('__')]
        for s in settings_attrs:
            if not hasattr(settings, s):
                setattr(settings, s, getattr(temp_set, s))
        
        self.extractModelFileTextbox.setText(settings.cur_model_path)
        self.extractOutputTextbox.setText(settings.cur_output_dir)
        self.settings = settings
    
    
    def saveSettings(self):
        """Return state of settings back to caller."""
        
        self.settings.cur_model_path = str(self.extractModelFileTextbox.text())
        self.settings.cur_output_dir = str(self.extractOutputTextbox.text())
        return self.settings


class ToolSettings(object):
    """Store the settings used by this class."""
    
    def __init__(self):
        
        self.tool_name = 'Model Extractor'
        self.cur_model_path = ''
        self.cur_output_dir = ''
        self.cur_location = ''
        





