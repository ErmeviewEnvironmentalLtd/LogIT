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
     DR (28/04/2016):
         Changed use of ToolSettings class to use of a dictionary instead. This
         should cause less hassle when additional variables need to be added.
         Also now shares the path_holder dict in globalsettings.py.
         Now using the AWidget interface.
     DR (16/06/2-16):
         Add run options input textbox and logic for dealing with run options.
         When run options are supplied the user can choose between either 
         copying all files in the model and maintaining the original setup of
         the control files, or hardcoding the output control files and only
         copying the files specified by the run options.

 TODO:
     (12/06/16): Some files are being added to the in and out lists twice.
     It doesn't actually cause an issue, but should be fixed to avoid possible
     copy problems and increases run times.
    

###############################################################################
"""

import os
import shutil
import re

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from ship.utils.filetools import MyFileDialogs
from ship.utils.fileloaders.fileloader import FileLoader
from ship.tuflow.data_files import datafileloader
from ship.utils import filetools
from ship.tuflow import FILEPART_TYPES as fpt
from ship.utils import utilfunctions as uf
    
from AWidget import AWidget
import ModelExtractor_Widget as extractwidget
logger.debug('ModelExtractor_Widget import complete')
from app_metrics import utils as applog
import globalsettings as gs


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



class ModelExtractor_UI(extractwidget.Ui_ExtractModelWidget, AWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        
        AWidget.__init__(self, 'Model Extractor', cwd, parent, f)
        self.setupUi(self)
        
        # Connect the slots
        self.extractModelFileButton.clicked.connect(self._setInputFile)
        self.extractOutputButton.clicked.connect(self._setOutputDirectory)
        self.extractModelButton.clicked.connect(self._extractModel)
        
        self.setupLookupLists()
    

    def _setInputFile(self):
        """Get the input model file to use."""

        if 'model' in gs.path_holder.keys():
            path = gs.path_holder['model']
        else:
            path = self.cur_location

        d = MyFileDialogs(parent=self)
        open_path = d.openFileDialog(path, file_types='Ief/Tcf File(*.ief;*tcf)')
        if open_path == False:
            return
        
        open_path = os.path.normpath(str(open_path))
        self.extractModelFileTextbox.setText(open_path)
        gs.setPath('model', open_path)
        
    
    def _setOutputDirectory(self):
        """Set the directory to extract the model to."""

        if 'output' in gs.path_holder.keys():
            path = gs.path_holder['output']
        else:
            path = self.cur_location

        d = MyFileDialogs(parent=self)
        dir_path = d.dirFileDialog(path)
        if dir_path == False:
            return
        dir_path = str(dir_path)
        # Make sure we don't accidentally write over input files
        if 'model' in gs.path_holder.keys():
            if dir_path == os.path.normpath(os.path.split(gs.path_holder['model'])[0]):
                message = ('It looks like the output directory matches the ' +
                           'model directory.\n This can lead to files being ' +
                           'overwritten.\n Are you sure?')
                response = self.launchQtQBox('Directory Match', message)
                if response == False:
                    return
        
        dir_path = os.path.normpath(str(dir_path))
        self.extractOutputTextbox.setText(dir_path)
        gs.setPath('output', dir_path)
    
    def _extractModel(self):
        """Extract the given model.
        
        Calls two functions to setup and find the file and then to write them
        to the new location.
        """
        in_path = str(self.extractModelFileTextbox.text())
        out_dir = str(self.extractOutputTextbox.text())
        
        if not os.path.exists(in_path):
            logger.error('Model file does not exist')
            QtGui.QMessageBox.warning(self, "File not found",
                                      "Model file does not exist")
            return
            
        if not os.path.exists(out_dir):
            logger.error('Output directory does not exist')
            QtGui.QMessageBox.warning(self, "Directory not found",
                                      "Output directory does not exist")
            return

        success, tuflow_files = self._extractModelSetup(in_path, out_dir)
        if success:
            success = self._extractModelWrite(tuflow_files)

        self._displayOutput(in_path, out_dir)
        self.emit(QtCore.SIGNAL("updateProgress"), 0)
        self.emit(QtCore.SIGNAL("statusUpdate"), '')
        
        # Log use on the server
        if not gs.__DEV_MODE__:
            applog.AppLogger().write('Extractor')
    
    def _extractModelSetup(self, in_path, out_dir):
        """Finds all the files and re-writes the file path variables."""

        self._extractVars = ExtractVars()
        self.extractOutputTextArea.clear()
        self._extractVars.out_dir = out_dir
        self._extractVars.hardcode = self.extractorHardcodeFilesCbox.isChecked()
        
        se_vals = str(self.extractRunOptionsTextbox.text())
        if not se_vals == '':
            self.se_vals = uf.convertRunOptionsToSEDict(se_vals)
        else:
            self.se_vals = {}
            self._extractVars.hardcode = False
        
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
            self._extractVars.tuflow = loader.loadFile(self._extractVars.tcf_path,
                                                       self.se_vals)
            self._loadModelFiles()
            
            success = self._updateModelFilePaths() 
            if not success:
                return False, None

            if self._extractVars.hardcode:
                tuflow_files = self._extractVars.tuflow.getPrintableContents(se_only=True)
            else:
                tuflow_files = self._extractVars.tuflow.getPrintableContents()
            
            i=0
        
        elif not self._extractVars.has_tcf:
            logger.error('Model has found tcf but tcf_path is None')
            QtGui.QMessageBox.warning(self, "Tcf is None",
                                      "Model has found tcf but tcf_path is None")
            return False, None
        
        #DEBUG
#         for k, t in tuflow_files.items():
#             filetools.writeFile(t, k)
        
            
        return True, tuflow_files
        
    
    def _extractModelWrite(self, tuflow_files):
        """Writes out all the updated files to the new location."""
        
        # Get the input and output files together and copy everything
        combo_files = self._mergeFiles() 
        self._writeOutResultsFiles() 
        success = self._writeOutModelFiles(combo_files)
        if not success:
            logger.error('File paths have corrupted in load')
            QtGui.QMessageBox.warning(self, "File path corruption",
                                      "Some in-filenames do not mach out-filenames.\nThis has corrupted the copy attempt")
            return False
        
        if not self._extractVars.ief == None:
            contents = self._extractVars.ief.getPrintableContents()
            p = self._extractVars.ief.path_holder.getAbsolutePath()
            d = os.path.split(p)[0]
            if not os.path.exists(d):
                os.makedirs(d, 0777)
            filetools.writeFile(contents, 
                                self._extractVars.ief.path_holder.getAbsolutePath())
        
        if not self._extractVars.tcf_path == None:
            for path, contents in tuflow_files.iteritems():
                filetools.writeFile(contents, path)
        
        return True
        
    
    def _displayOutput(self, infile, outdir):
        """
        """
        output = []
        output.append('\n Model extraction complete.')
        output.append('  Input file: ' + os.path.normpath(infile))
        output.append('  Output directory: ' + os.path.normpath(outdir))
        
        if self._extractVars.failed_data_files:
            output.append('\n\nUnable to load some datafiles - These may contain references to other files which have not been found.')
            output.append('The following files could not be loaded:\n')
            for d in self._extractVars.failed_data_files:
                output.append(d) 

        if self._extractVars.missing_model_files:
            output.append('\n\nCould not copy some model files - check that they exist.')
            output.append('The following files could not be copied:\n')
            for m in self._extractVars.missing_model_files:
                output.append(os.path.normpath(m)) 
        
        if self._extractVars.missing_results_files:
            output.append('\n\nCould not copy some results files - check that they exist.')
            output.append('The following files could not be copied:\n')
            for r in self._extractVars.missing_results_files:
                output.append(os.path.normpath(r)) 
                
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
                        if not os.path.split(p[1])[1] == f:
                            os.chdir(curd)
                            return False
                        
                        os.chdir(d)
                        self.emit(QtCore.SIGNAL("updateProgress"), i)
                        
                        extstuff = os.path.splitext(f)
                        if len(extstuff) > 1 and (extstuff[1] == '.asc' or extstuff[1] == '.txt'): 
                            self.emit(QtCore.SIGNAL("statusUpdate"), 'Copying Grid file, this may take a while...')
                            shutil.copy(f, p[1])
                            self.emit(QtCore.SIGNAL("statusUpdate"), 'Copying model files...')
                        else:
                            shutil.copy(f, p[1])
                except IOError:
                    self._extractVars.missing_model_files.append(p[0])

            else:
                self._extractVars.missing_model_files.append(p[0])

        os.chdir(curd)
        return True
    
    
    def checkIfRightFile(self, filename, file_to_check):
        """Check to see if we have a result file that we need.
        
        It can be a bit complicated so there are probably some issues here,
        but at the moment it seems to do ok.
        If there is only an extension after the known name, or the rest 
        before the extension matches a known ending it will return True.
        """
        
        try:
            # If it's a projection file
            if file_to_check == 'Projection.prj': return True
            
            parts = file_to_check.split(filename)
            
            # If it's only the filename matched exactly
            if len(parts) < 2:
                return False
            # If second part is the start of the extension
            if parts[1].startswith('.'):
                return True
            
            subparts = parts[1].split('.')
            if len(subparts) < 2:
                return False
            # If the extra bit before extension is an '_' followed by three
            # numbers (matches isis run output .bmp's)
            if re.match(r'[_]\d{3}', subparts[0]):
                return True
            # If bit before extension is in the known check/result file endings
            if subparts[0] in self.check_list or subparts[0] in self.result_list:
                return True
        except:
            pass
        
        return False
    
    
    def _writeOutResultsFiles(self): 
        """Copy the result files into the new directory.
        """
        curd = os.getcwd()
        results_names_in = []
        results_names_out = []
        
        no_results_folders = len(self._extractVars.results_files)
        for i, r in enumerate(self._extractVars.results_files, 1):
            self.emit(QtCore.SIGNAL("statusUpdate"), 
                      ('Copying output folder %s of %s (Some results can take a while)' % (i, no_results_folders)))
            old_p, old_n = os.path.split(r[0])
            new_p, new_n = os.path.split(r[1])
            
            if not os.path.exists(old_p):
                logger.warning('Could not copy results from: ' + old_p)
                self._extractVars.missing_results_files.append('Could not read results from: ' + old_p)
                continue
            
            file_list = os.listdir(old_p)
            
            try:
                if not os.path.exists(new_p):
                    os.makedirs(new_p, 0777)
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
                if self.checkIfRightFile(old_n.upper(), f.upper()):
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
        results_files = model_file.getFiles(fpt.RESULT)
        for r in results_files:
            paths = r.getAbsolutePath(all_types=True)
            
            if r.command.upper() == 'OUTPUT FOLDER':
                if model_file.TYPE == 'tcf':
                    new_root = r'..\results\2d'
                else:
                    new_root = r'..\results\1d'
            
            elif r.command.upper() == 'WRITE CHECK FILES':
                new_root = r'..\checks'
            
            elif r.command.upper() == 'LOG FOLDER':
                new_root = r'logs'
            
            # Update the file paths. Check files are treated differently
            # because they can have a prefix as part of the file name
            if r.command.upper() == 'WRITE CHECK FILES':
                in_name = os.path.join(r.root, r.parent_relative_root,
                                       r.relative_root)
                out_name = os.path.join(self._extractVars.out_dir, 
                                          new_root)
                if r.file_name_is_prefix:
                    in_name = os.path.join(in_name, r.file_name)
                    out_name = os.path.join(out_name, r.file_name)
                else:
                    in_name = os.path.join(in_name, run_name)
                    out_name = os.path.join(out_name, run_name)
            else:
                in_name = os.path.join(r.root, r.parent_relative_root,
                                       r.relative_root, run_name)
                out_name = os.path.join(self._extractVars.out_dir, 
                                          new_root, run_name)
            
            self._extractVars.results_files.append([in_name, out_name])
            r.relative_root = new_root
            r.parent_relative_root = rel_root
            r.root = ''
        

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
        if self._extractVars.hardcode:
            data_files = model_file.getFiles(fpt.DATA, se_vals=self.se_vals)
        else:
            data_files = model_file.getFiles(fpt.DATA)

        for d in data_files:
            paths = d.getAbsolutePath(all_types=True)

            # Don't add the same files twice
            #if paths[0] in self._extractVars.in_files:
            self._extractVars.in_files.extend(d.getAbsolutePath(all_types=True))
            
            subfiles_in = []
            subfiles_out = []
            if not d.extension == 'tmf':
                
                success, subfiles_in, subfiles_out = self._getSourceFiles(d, 
                                        r'..\bc_dbase', model_root, rel_root)
                if not success:
                    self._extractVars.failed_data_files.append(d.getAbsolutePath()) 

            d.parent_relative_root = rel_root
            d.root = self._extractVars.out_dir
            
            if d.command.upper() == 'BC DATABASE':
                d.relative_root = os.path.join(model_root, source_root)
            
            elif d.command.upper() == 'READ MATERIALS FILE':
                d.relative_root = model_root
            
            #if paths[0] in self._extractVars.in_files: continue
            
            self._extractVars.out_files.extend(d.getAbsolutePath(all_types=True))
            self._extractVars.in_files.extend(subfiles_in)
            self._extractVars.out_files.extend(subfiles_out)


    def _fetchGisFiles(self, model_file, source_root, main_root, rel_root, model_root): 
        """Get all of the data files and any subfiles they contain.
        
        Attempts to load any data files (.tmf, .csv, etc) and checks to see if
        they contain references to any subfiles. If they do it calls 
        getSourceFiles() to create the in and out paths for them as well.
        
        Args:
            model_file(TuflowModelFile): the model file being read.
            source_root(str): location to set for the out file.
            main_root(str): location to set for the gis file, which may be 
                different to that for the subfiles.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
        
        """
        if self._extractVars.hardcode:
            gis_files = model_file.getFiles(fpt.GIS, se_vals=self.se_vals)
        else:
            gis_files = model_file.getFiles(fpt.GIS)
        for g in gis_files:
            paths = g.getAbsolutePath(all_types=True)
            
            # Don't add the same files twice
            #if paths[0] in self._extractVars.in_files:
            self._extractVars.in_files.extend(g.getAbsolutePath(all_types=True))
        
            subfiles_in = []
            subfiles_out = []
            if g.command.upper() == 'READ MI TABLE LINKS':
                
                success, subfiles_in, subfiles_out = self._getSourceFiles(g, 
                                                    'xs', model_root, rel_root)
                if not success:
                    self._extractVars.failed_data_files.append(g.getAbsolutePath()) 

                g.relative_root = os.path.join(model_root, source_root)

            elif g.command.upper().startswith('READ GRID'):
                g.relative_root = os.path.join(model_root, 'grid')

            else:
                g.relative_root = os.path.join(model_root, main_root)
                
            g.parent_relative_root = rel_root

            g.root = self._extractVars.out_dir
            
            #if paths[0] in self._extractVars.in_files: continue 
            
            self._extractVars.out_files.extend(g.getAbsolutePath(all_types=True))
            self._extractVars.in_files.extend(subfiles_in)
            self._extractVars.out_files.extend(subfiles_out)
    
    
    def _getSourceFiles(self, data_file, source_root, model_root, rel_root): 
        """Get all of the sub files contained by a data file.
        
        Loads the given TuflowFile reference and checks to see if it contains
        any references to other files. If it does it gets/sets the in/out file
        locations.
        
        Args:
            data_file(TuflowFile): the ATuflowFilePart.
            source_root(str): location to set for the out file.
            rel_root(str): the relative path to set for the files.
            model_root(str): the relative path of the model file to set.
        """
        missing_files = []
        subfiles_in = []
        subfiles_out = []
        try:
            logger.debug('Datafile = ' + str(data_file.file_name))
            dobj = datafileloader.loadDataFile(data_file)

            try:
                i = dobj.keys.SOURCE
            except AttributeError:
                return False, [], []
            
            source = dobj.row_collection.getRowDataAsList(dobj.keys.SOURCE)
            for s in source:
                # Create a path holder
                f = filetools.PathHolder(s, data_file.root)
                f.relative_root = data_file.relative_root
                subfiles_in.append(f.getAbsolutePath())
                
                f.relative_root = os.path.join(model_root, source_root)
                f.parent_relative_root = rel_root
                f.root = self._extractVars.out_dir
                subfiles_out.append(f.getAbsolutePath())
                
        except (IOError, IndexError, AttributeError):
            return False, [], []
        
        return True, subfiles_in, subfiles_out

    
    def _updateModelFilePaths(self): 
        """Update the paths of the ATuflowModelFiles (tcf, tgc, etc).
        
        These are being read and updated for the new location so it is
        important that they don't overwrite the existing versions. The paths
        before update are checked against those after update to ensure that 
        this can't happen. If there's an issue we stop and retreat.
        """
        out_name_check = []
        in_name_check = []
        
        # Maybe play it safe here and update all of the files just in case?
        # It would avoid accidentally overwriting a file if something went wrong
#         if self._extractVars.se_only:
#             model_files = self._extractVars.tuflow.getModelFiles(se_only=True)
#         else:
#             model_files = self._extractVars.tuflow.getModelFiles()
        model_files = self._extractVars.tuflow.getModelFiles()
        
        try:
            for key, models in model_files.items():
                for m in models:
                    in_name_check.append(m.root)
                    m.parent_relative_root = r''
                    m.root = self._extractVars.out_dir
                    out_name_check.append(m.root) 
        except:
            logger.error('Problem changing paths - aborting to avoid overwriting file!')
            return False
        
        # Make sure all paths have been updated.
        for o in out_name_check:
            if o in in_name_check:
                logger.warning('Some file paths have failed to update - Aborting to avoid overwriting files!')
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
        run_name = self._extractVars.tuflow.mainfile.file_name
        if not self.se_vals == {}:
            run_name = uf.getSEResolvedFilename(run_name, self.se_vals)
        
        if self._extractVars.hardcode:
            model_files = self._extractVars.tuflow.getTuflowModelFiles(se_only=True)
        else:
            model_files = self._extractVars.tuflow.getTuflowModelFiles()

        for key, model_list in model_files.items():
            for m in model_list:
                if  key == 'tcf' or key == 'ecf' or key == 'tef':
                    model_root = r'..\model'
                    rel_root = r''
                else:
                    model_root = r''
                    rel_root = r'..\model'
                
                self._fetchGisFiles(m[0], 'xs', 'gis', rel_root, model_root)
                self._fetchDataFiles(m[0], r'..\bc_dbase', rel_root, model_root)
                self._fetchResultsFiles(m[0], rel_root, model_root, run_name)
            
    
    def _getIsisFiles(self): 
        """Get all of the ISIS/FMP related files from the ief.
        
        Any reference to any file components in the ief is stored.
        """
        loader = FileLoader()
        self._extractVars.ief = loader.loadFile(self._extractVars.ief_path)
        
        if '2DFile' in self._extractVars.ief.event_details.keys():
            scheme = self._extractVars.ief.getValue('2DScheme')
            if scheme == 'Tuflow':
                self._extractVars.tcf_path = self._extractVars.ief.event_details['2DFile']
                out_tcf = os.path.split(self._extractVars.tcf_path)[1]
                self._extractVars.ief.event_details['2DFile'] = os.path.join(r'..\..\tuflow\runs', out_tcf)
                self._extractVars.has_tcf = True
                
                # Get 2D run options str if found and convert to correct format
                options = self._extractVars.ief.getValue('2DOptions')
                if not options is None:
                    self.se_vals = uf.convertRunOptionsToSEDict(options)
                else:
                    self.se_vals = {}
        
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
            self._extractVars.ief.event_header['Results'] = os.path.join(r'..\results', f)
        
        for i, ied in enumerate(self._extractVars.ief.ied_data):
            ied_in = ied['file']
            ied_name = os.path.split(ied_in)[1]
            self._extractVars.ief.ied_data[i]['file'] = os.path.join(r'..\ieds', ied_name)
            self._extractVars.in_files.append(ied_in)
            self._extractVars.out_files.append(os.path.join(self._extractVars.out_dir, r'fmp\ieds', ied_name))
        

        self._extractVars.ief.path_holder.root = os.path.join(self._extractVars.out_dir, 'fmp', 'iefs')


    def setupLookupLists(self):
        """
        """
        
        self.result_list = [
        '_D',
        '_D_EXTENT',
        '_D_FE',
        '_DMAX_G002',
        '_H',
        '_HMAX_G002',
        '_MB',
        '_MB2D',
        '_PO',
        '_Q',
        '_V',
        '_ZUK1',
        '_ZUK0',
        '_1D_H',
        '_1D_MB',
        '_1D_MMH',
        '_1D_MMQ',
        '_1D_MMV',
        '_1D_MMD',
        '_1D_Q',
        '_1D_V',
        '_1D_D',
        '_1D_H',
        '_MB1D',
        '_TS',
        '_TSF',
        '_TSMB',
        '_TSMB1D2D',
        '_MESSAGES']
        
        self.check_list = [
        '_2D_BC_TABLES_CHECK',
        '_BCC_CHECK',
        '_BCC_CHECK_R',
        '_DEM_M',
        '_DEM_M',
        'DEM_Z',
        '_DEM_Z',
        '_DOM_CHECK',
        '_DOM_CHECK_R',
        '_FC_CHECK',
        '_FC_CHECK_R',
        '_FCSH_UVPT_CHECK',
        '_FCSH_UVPT_CHECK_P',
        '_GLO_CHECK',
        '_GLO_CHECK_P',
        'GRD_CHECK'
        '_GRD_CHECK',
        '_GRD_CHECK_R',
        '_INPUT_LAYERS',
        '_LFCSH_UVPT_CHECK',
        '_LFCSH_UVPT_CHECK_P',
        '_LP_CHECK',
        '_LP_CHECK_L',
        '_PO_CHECK',
        '_PO_CHECK_P',
        '_PO_CHECK_L',
        '_SAC_CHECK',
        '_SAC_CHECK_R',
        '_SH_OBJ_CHECK',
        '_SH_OBJ_CHECK_R',
        '_UVPT_CHECK',
        '_UVPT_CHECK_P',
        '_VZSH_CHECK',
        '_VZSH_CHECK_P',
        '_VZSH_CHECK_L',
        '_ZLN_ZPT_CHECK',
        '_ZLN_ZPT_CHECK_P',
        '_ZPT_CHECK',
        '_ZPT_CHECK_P',
        '_ZSH_ZPT_CHECK',
        '_ZSH_ZPT_CHECK_P',
        '_1D_BC_TABLES_CHECK',
        '_PIT_INLET_TABLES_CHECK',
        '1D_TA_TABLES_CHECK',
        '_BC_CHECK',
        '_BC_CHECK_P',
        '_HYDROPROP_CHECK',
        '_HYDROPROP_CHECK_L',
        '_INVERTS_CHECK',
        '_INVERTS_CHECK_P',
        '_IWL_CHECK',
        '_IWL_CHECK_P',
        '_MHC_CHECK',
        '_MHC_CHECK_P',
        '_NWK_C_CHECK',
        '_NWK_C_CHECK_L',
        '_NWK_N_CHECK',
        '_NWK_N_CHECK_P',
        '_WLLO_CHECK',
        '_WLLO_CHECK_L',
        '_XWLLO_CHECK',
        '_XWLLO_CHECK_L',
        '_WLLP_CHECK',
        '_WLLP_CHECK_P',
        '_XWLLP_CHECK',
        '_XWLLP_CHECK_P',
        '_XSL_CHECK',
        '_XSL_CHECK_L',
        '_X1D_CHANS_CHECK',
        '_X1D_CHANS_CHECK_L',
        '_X1D_NODES_CHECK',
        '_X1D_NODES_CHECK_P',
        '_1D_TO_2D_CHECK',
        '_1D_TO_2D_CHECK_R',
        '_X1D_H_TO_2D',
        '_X1D_H_FROM_2D',
        '_2D_Q_TO_X1D',
        '_2D_Q_FROM_X1D',
        '_2D_TO_2D_CHECK',
        '_2D_TO_2D_CHECK_R']





