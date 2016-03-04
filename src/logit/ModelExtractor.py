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

# Standard modules
import os

# tmac_tools modules
from tmac_tools_lib.utils.fileloaders.fileloader import FileLoader
from tmac_tools_lib.tuflow.tuflowfilepart import SomeFile
from tmac_tools_lib.tuflow.data_files import datafileloader
from tmac_tools_lib.utils import filetools


def extractModel(output_dir, tcf_path, ief_path, run_row, errors):
    """
    """
    loader = FileLoader()

    # Read the Ief file in and get the file paths to everything else
#     ief_path = os.path.join(curd, '..', r'tmac_tools\tests\testinputdata\Model\isis\iefs\Kennford_v1.5.ief')
    
    if not ief_path == None:
        all_paths, tcf_path, out_tcf_path = getIefFilePaths(ief_path)

    # Get the new root to the tcf file for prepending to tuflow model files
    new_root = filetools.getDirectory(out_tcf_path)

    # Create the tuflow tcf object
    tuflow_model = loader.loadFile(in_tcf_path)

    # Get the root and files for the existing setup
    old_root = tuflow_model.root
    old_paths = tuflow_model.getAbsolutePaths(all_types=True)
    
    # Need to update any DATA_FILE paths as well
    # This must be done before the changeRoot() function is called or
    # we won't be able to load the file.
    data_files = tuflow_model.contents(content_type=tuflow_model.DATA)
    
    old_data_paths = []
    new_data_paths = []
    for d in data_files:
        data_obj = datafileloader.loadDataFile(d)
        old_data_paths += data_obj.getAllPaths(include_this=False)            
        data_obj.changeRoot(new_root)
        new_data_paths += data_obj.getAllPaths(include_this=False)
         
    # Get the root and files for the new setup
    tuflow_model.changeRoot(new_root)
    new_paths = tuflow_model.getAbsolutePaths(all_types=True)

    # Now add the datafile paths
    for i, p in enumerate(old_data_paths):
        old_paths.append(p)
        new_paths.append(new_paths[i])

    # Add the root onto the file paths and add to all_paths
    for i, p in enumerate(old_paths):
        all_paths.append({'old': p, 'new': new_paths[i]})

    # Write it all to disk
    writeNewModelLocation(all_paths)


def getIefFilePaths(ief_path, output_dir):
    """Loads an .ief file and extracts all the file paths from it.
    
    Args:
        ief_path (str): the absolute path to the ief file.
        
    Return:
        tuple - containing:  
            * list: all the files found.
            * string: the existing tcf file path.
            * string: the updated tcf file path (for new location)
    """

    # Setup the ief paths
    in_ief_path = ief_path
    out_ief_path = os.path.join(output_dir, 'isis', 'iefs', 'Kennford_v1.5.ief')

    # Load the ief file and get the paths
    ief = loader.loadFile(in_ief_path)
    paths  = ief.getFilePaths()

    # Get the dat file path and set the new one
    in_dat_path = paths[0]['datafile']
    out_dat_path = os.path.join(output_dir, 'isis', 'datafiles', os.path.split(in_dat_path)[1])

    # Get the initial conditions path and set the new one
    in_ic_path = paths[0]['initialconditions']
    out_ic_path = os.path.join(output_dir, 'isis', 'datafiles', os.path.split(in_ic_path)[1])

    # Get the tuflow tcf file path and set the new one
    in_tcf_path = paths[0]['twodfile']
    tcf_name = filetools.getFileName(in_tcf_path, with_extension=True)
    out_tcf_path = os.path.join(output_dir, 'tuflow', 'runs', tcf_name)

    # Add the Tcf file on
    all_paths = []
    all_paths.append({'old': in_tcf_path, 'new': out_tcf_path})
    all_paths.append({'old': in_ief_path, 'new': out_ief_path})
    all_paths.append({'old': in_dat_path, 'new': out_dat_path})
    all_paths.append({'old': in_ic_path, 'new': out_ic_path})

    return all_paths, in_tcf_path, out_tcf_path


def writeNewModelLocation(model_paths):
    """Write out the model to the new directory.
    
    Loop through all of the paths that we grabbed copying them from the
    original file paths into the new one. If the directories that we are
    copying to don't exist we make them. If there is an error finding the
    file to copy or it can't be saved to the new list make a record of it
    to display to the user.
    """
    
    print '\n******************************************************************'
    print '*'
    print '* NOTE:'
    print '*   Result and Check files will show as "Not Found" and "Not' 
    print '*   Moved". This is because in most cases they are only a' 
    print '*   directory and not a file.'
    print '*   At the moment this tool does not move either of these groups'
    print '*   of files into the new directory.'
    print '*'
    print '******************************************************************'
    
    not_moved = []
    for p in all_paths:
        tester = os.path.exists(p['old'])
        if os.path.exists(p['old']):

            try:
                d = os.path.dirname(p['new'])
                if not os.path.exists(d):
                    os.makedirs(d, 0777)
            except IOError:
                print 'Cannot make directory for: ' + p['new']
                continue

            try:
                if not os.path.isdir(p['old']):
                    shutil.copy(p['old'], p['new'])
            except IOError:
                print 'Cannot copy file: ' + p['old']
                not_moved.append(p['old'])

        else:
            print 'File not found: ' + p['old']
            not_moved.append(p['old'])

    print '\nFiles not moved:'
    for f in not_moved:
        print f


