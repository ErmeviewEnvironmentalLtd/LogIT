"""
##############################################################################
  Name: LogIT (Logger for Isis and Tuflow) 
  Author: Duncan Runnacles
  Copyright: (C) 2016 Duncan Runnacles
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
 
 
  Module:          logit.py
  Date:            28/03/2016
  Author:          Duncan Runnacles
  Since-Version:   0.5
  
  Summary:
      Tools for resolving .ief file filepaths. Contains functions for 
      attempting to automate the update of file paths from their original
      location to the location that the model has been moved to. These include
      an initial attempt at automating the process and a secondary approach at
      trying to find the files by walking the directories. If the second 
      approach is used it may not find the correct version of the file.
 
  UPDATES:

  TODO:
     
############################################################################## 
"""

import os
import sys
import shutil

from PyQt4 import QtGui

from ship.utils.fileloaders import fileloader as fl
from ship.utils.qtclasses import MyFileDialogs
from ship.utils import filetools as ft

import logging
logger = logging.getLogger(__name__)


class IefResolverDialog(QtGui.QDialog):
    """Dialog class for showing ief resolver summary information."""
    
    def __init__(self, input, parent=None):
        super(IefResolverDialog, self).__init__(parent)
        
        self.textBrowser = QtGui.QTextBrowser(self)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        
        output = []
        output.append(self.getOpeningRichText())
        output.extend(self.formatOutput(input))
        output.append(self.getClosingRichText())
        output = ''.join(output)
        self.textBrowser.setText(output)
    
    
    def formatOutput(self, input):
        """Get the input dict and format for display."""
        formatted = []
        msg = ("I've managed to update most of your files but some " +
                 "of them needed to be searched for. This can lead to " +
                 "incorrectly updated files.<br />Where an updated file is " +
                 "shown as 'False' it could not be found and must be " +
                 "manually updated. <br />You should check the " +
                 "updates. There is a summary below.\n\n\n")
        formatted.append(self.getSpaceParagraphIn() + msg + self.getStandardParagraphOut())
        for k, v in input.iteritems():
            
            if len(v['in']) < 1: continue
            formatted.append(self.getStandardParagraphIn() + '<em style="font-weight: bold">Some paths required guessing for file</em>: ' + k + self.getStandardParagraphOut())
            inner_msg = ("You should check that these are correct. It " +
                             "may be that the files don't exist or are " +
                             "outside the searched folders.")
            formatted.append(self.getSpaceParagraphIn() + inner_msg + self.getStandardParagraphOut())
            for i, p in enumerate(v['in']):
                formatted.append(self.getStandardParagraphIn() + '<em style="font-weight: bold">Original:</em> ' + p + self.getStandardParagraphOut())
                formatted.append(self.getStandardParagraphIn() + '<em style="font-weight: bold">Updated:</em> ' + str(v['out'][i]) + self.getStandardParagraphOut())
            
            formatted.append('<br /><br />')
        
        return formatted

    
    def getStandardParagraphIn(self):
        """Standard display paragraph."""
        return '''
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
<span style=" font-size:10pt;">
'''
        

    def getSpaceParagraphIn(self):
        """Standard display paragraph but with space at the bottom."""
        return '''
<p style=" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
<span style=" font-size:10pt;">
'''


    def getStandardParagraphOut(self):
        """Close standard paragraph elements."""
        return '</span></p>'
    
    
    def getOpeningRichText(self):
        """Opening headers etc for using rich text."""
        return '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Arial'; font-size:10pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:20px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt; font-weight:600; text-decoration: underline;">Ief Resolver Summary</span></p>
<ul>
'''
        

    def getClosingRichText(self):
        """Closes tags for the opening elements."""
        return '</ul></body></html>'



class IefHolder(object):
    
    def __init__(self, ief_obj):
        self.ief_obj = ief_obj
        self.original_path = ief_obj.path_holder.getAbsolutePath()
        self.root_folder_old = ''
        self.root_folder_new = ''
        self.result_name = ''
        self.single_types = {'.dat': {'in': '', 'out': ''}, 
                             '.tcf': {'in': '', 'out': ''},
                             'result': {'in': '', 'out': ''}
                            }
        self.ieds_list_types = {'in': [], 'out': []}
        self.missing_types = {'.tcf': True, '.dat': True, '.ied': True, 'result': True}
        self.has_types = {'.tcf': False, '.dat': False, '.ied': False, 'result': False}
        self.selected_paths = {'.tcf': '', '.dat': '', '.ied': '', 'result': ''}
    
    
    def getUpdatedIefObj(self):
        """Update the Ief object with the setup held by this class.
        
        Return:
            Ief - updated with the path variables held by this class.
        """
        p, e = os.path.splitext(self.ief_obj.path_holder.getAbsolutePath())
        p = p + '_LOGIT' + e
        self.ief_obj.path_holder.setPathsWithAbsolutePath(p)
        
        for k, v in self.single_types.iteritems():
            if k == '.dat':
                if v['out'] == '': continue
                self.ief_obj.event_header['Datafile'] = v['out']            
            if k == '.tcf':
                if v['out'] == '': continue
                self.ief_obj.event_details['2DFile'] = v['out']            
            if k == 'result':
                if v['out'] == '': continue
                self.ief_obj.event_header['Results'] = os.path.join(v['out'], self.result_name)            
        
        for i, ied_out in enumerate(self.ieds_list_types['out']):
            if ied_out == '': continue
            self.ief_obj.ied_data.append(ied_out)
        
        return self.ief_obj
        
    
    def addFile(self, new_file, in_or_out, test_exists=True):
        """Add a file path to object.
        
        If test_exists == True the file will be checked to see if it exists 
        and is findable. If this test fails the function will return False.
        """
        extstuff = os.path.splitext(new_file)
        if len(extstuff) < 2 or extstuff[1] == '':
            ext = ''
        else:
            ext = extstuff[1].lower()
        if not ext in self.single_types.keys() and not ext == '.ied':
            if not os.path.exists(new_file): return False
            if in_or_out == 'out': 
                self.missing_types['result'] = False
            else:
                self.has_types['result'] = True
            self.single_types['result'][in_or_out] = new_file
        
        elif ext == '.ied':
            if not os.path.exists(new_file): return False
            if in_or_out == 'out': 
                self.missing_types['.ied'] = False
            else:
                self.has_types['.ied'] = True
            self.ieds_list_types[in_or_out] = new_file
        
        else:
            if not os.path.exists(new_file): return False
            if in_or_out == 'out': 
                self.missing_types[ext] = False
            else:
                self.has_types[ext] = True
            self.single_types[ext][in_or_out] = new_file
        
        return True
 
 
    def getMissingFileKeys(self):
        """Get a list of the keys that contain no output file data.
        
        Return:
            list - keys of the file types that couldn't be set.
        """
        missing = []
        for k, v in self.missing_types.iteritems():
            if self.has_types[k] == True and v == True:
                missing.append(k)
        return missing



def updateIefObjects(ief_holders):
    """Update the Ief objects held by the ief_holders in the list.
    
    Calls the update function on each of the IefHolder objects held by the
    list and returns the updated  Ief classes.
    
    Args:
        ief_holders(list): IefHolder objects to update.
    
    Return:
        list - Ief objects with updated file variables.
    """
    ief_objs = []
    for ief_holder in ief_holders:        
        ief_objs.append(ief_holder.getUpdatedIefObj())
    
    return ief_objs


def writeUpdatedFiles(ief_objs):
    """Write out Ief objects to file.
    
    Uses the path variable held by the PathHolder object of the Ief. No check
    is made to see if the file already exists. If it does it will be overwritten.
    
    Args:
        ief_objs(list): containing Ief instances.
    
    Raises:
        IOError - when there's a problem writing to file.
    """    
    for ief in ief_objs:
        contents = ief.getPrintableContents()
        try:
            ft.writeFile(contents, ief.path_holder.getAbsolutePath())
        except IOError:
            logger.error('Could nto write new ief file at:\n' + ief.path_holder.getAbsolutePath())
            return False
    return True
    

def resolveUnfoundPaths(ief_holders):
    """Try to locate any files that couldn't be found with the initial approach.
    
    This is a last ditch attempt at trying to find any files that are missing.
    It walks through all of the nearby folders, starting four folders up from
    the location of the ief file to see if it can find a file with that name.
    
    It should be noted that if there are additional folders (backups or old
    runs for instance) that contain the file it may find one of those instead.
    That's why this is a last ditch attempt rather than the initial approach.
    
    A dictionary containing the original (in) and new (out) file lists will be
    returned alongside the IefHolder's list. This can be used to review 
    whether the 
    
    Args:
        ief_holders(list): IefHolder instance with files to search for.
    
    Return:
        Tuple(list, dict): list of updated IefHolder instances. Dict of lists
            containing the original and updated file names of any files that
            had to be looked for with this method.
    """
    had_to_search = {}
    for ief_holder in ief_holders:

        in_out_list = {'in': [], 'out': []}
        for k, v in ief_holder.missing_types.iteritems():
            
            # If it's a missing file
            if ief_holder.has_types[k] == True and v == True:
                file_out = False
                
                # If it's a .dat or .tcf file
                if k in ief_holder.single_types.keys() and not k == 'result':
                    infile = ief_holder.single_types[k]['in']
                    filename = os.path.split(infile)[1]
                    file_out = findFile(infile, filename)
                    in_out_list['in'].append(infile)
                    in_out_list['out'].append(file_out)
                    if not file_out == False:
                        ief_holder.addFile(file_out, 'out', False)
                
                elif k == '.ied':
                    for ied in ief_holder.ieds_list_types:
                        filename = os.path.split(ied['in'])[1]
                        file_out = findFile(ied['in'], filename)
                        in_out_list['in'].append(infile)
                        in_out_list['out'].append(file_out)
                        if not file_out == False:
                            ief_holder.addFile(file_out, 'out', False)
                
                # Otherwise it can only be a result file
                else:
                    infile = ief_holder.single_types['result']['in']
                    filename = os.path.split(infile)[1]
                    file_out = findFile(infile, filename)
                    in_out_list['in'].append(infile)
                    if not file_out == False:
                        in_out_list['out'].append(os.path.join(file_out, ief_holder.result_name))
                        ief_holder.addFile(file_out, 'out', False)
                    else:
                        in_out_list['out'].append(file_out)
                
        had_to_search[ief_holder.original_path] = in_out_list
    
    return ief_holders, had_to_search

        
def findFile(start_location, file_to_find, search_folder_depth=3,
             return_first_find=False):
    """Walk the folder structure until matching files are found.
    
    Args:
        start_location(str): path to the file or folder to start walking from.
        file_to_find(str): the name and extension of the file to look for.
        search_folder_depth=3(int): the number of folder to go up from the 
            start_location before walking down the directories.
        return_first_find=False(bool): if True will return only the first 
            matching file that it finds (as a list).
    
    Return:
        list - containg the normalised absolute paths of all of the files found.
            If return_first_find == True the list will only contain the first
            matching file found. 
        False - if no match could be found.
    """
    # Set the number of folders to search upwards from the ief file.
    # This will be the point we start walking down the path to find
    # the reference location (the location of the reference file)
    found_files = []
    folder_up = []
    for s in range(0, search_folder_depth):
        folder_up.append('..')
    folder_up = os.path.normpath('/'.join(folder_up))
    start_location = os.path.join(start_location, folder_up)

    for root, dir, files in os.walk(start_location):
        for f in files:
            splitted = os.path.split(f)
            if len(splitted) > 1 and splitted[1].lower() == file_to_find.lower():
                found_files.append(os.path.normpath(os.path.join(root, f)))
                if return_first_find:
                    return found_files
    
    if found_files:
        return found_files
    else:
        return False


def autoResolveIefs(iefs):
    """Attempt to automatically update the file paths in the given ief files.
    
    Tries to automatically update the file paths in a given ief file to work
    at the local directory. These may be ief files that have been moved from
    somewhere else and now need new absolute paths.
    
    First checks whether there is a 2D file referenced by the ief if there is
    that is set as the reference file, if not the .dat file is set as the
    reference file. The directories are walked to find this file at the number
    of folders above the ief file denoted by search_folder_depth. If this file
    cannot be found return False as it means any attempt at automating this is
    pretty much done. If it's found we derive a common path prefix for both
    the new location and the old location and use them to work out the new
    file paths by comparison and path masking.
    
    If any of the new paths created are found not to exist they are added to
    the missing files in the IefHolder and can be checked on return by calling
    the IefHolder's getMissingKeys() function.
    
    Args:
        iefs(list): filepaths to the ief files to be updated.
    
    Return:
        Tuple(Bool, list): True if Successful or False otherwise. List of
            IefHolder objects.
    """
    ief_holders = []
    for ief in iefs:
        success, new_holder = autoResolvePath(ief, search_folder_depth=4)
        if success:
            ief_holders.append(new_holder)
        else:
            return False, ief_holders
    
    return True, ief_holders
    
    
def autoResolvePath(ief_path, search_folder_depth=4):
    """Change the file names in an ief to match it's new location.
    
    Attempts to find a reference file to base the path prefix update on. The
    path prefix is the section of the old and new paths that is the same for
    all files referenced by the ief. This means that it expects all files to
    be under the same directory, which is usually the case when a model has
    been moved somewhere.
    
    Tries to find the reference file (2D if there is one, as this is likely 
    further from the ief file, of .dat if not) by walking the tree from the
    number of folders above the ief depicted by the search_folder_depth.
    
    Then udpates the file paths in the ief by matching and masking the old and
    new prefixes. It then checks if these guessed locations exist. If they 
    don't it will mark them as not found in the IefHolder instance.
    
    Args:
        ief_path(str): path to an ief file.
        seatch_folder_depth=4(int): number of directories to move up from the
            ief file before walking to find the reference file.
    
    Return:
        Tuple(Bool, IefHolder): False if reference file could not be found.
            IefHolder instance containing the status of the file updates.
    """
    loader = fl.FileLoader()
    ief_obj = loader.loadFile(ief_path)
    ief_holder = IefHolder(ief_obj)
    
    # Get the location of the ief file we just loaded
    cur_ief_location = os.path.split(ief_path)[0]
    
    # Get the dat and results paths from ief object
    ief_files_refs = ief_obj.getFilePaths()
    ief_datafile = ief_files_refs['Datafile']
    ief_holder.addFile(ief_datafile, 'in', test_exists=False)

    # Don't get the placeholder filename for the results
    ief_resultsfile, result_name = os.path.split(ief_files_refs['Results'])
    ief_holder.addFile(ief_resultsfile, 'in', test_exists=False)
    ief_holder.result_name = result_name
    in_paths = [ief_datafile, ief_resultsfile]
    
    '''If there's a 2d file then set it as the reference file. The reference
    file is the one we use to define the most 'upstream' folder. I.e. the
    root of all the model files. Use 2d if it's available because it will
    most likely define a more upstream folder location.
    '''
    if ief_files_refs['2DFile'] is not None:
        reference_file = ief_files_refs['2DFile']
        ief_holder.addFile(reference_file, 'in', test_exists=False)
        in_paths.append(ief_files_refs['2DFile'])
    else:
        reference_file = ief_files_refs['Datafile']
    ref_ext = os.path.splitext(reference_file)[1]

    # Get the folder of the reference file without the file name
    reference_file_folder, reference_file_file = os.path.split(reference_file)
    reference_file_folder = os.path.normpath(reference_file_folder)
    reference_file_file = os.path.normpath(reference_file_file)
    
    # Walk from given folder point upstream until we find the
    # reference files.
    reference_locations = findFile(ief_path, reference_file_file, 
                                  search_folder_depth) 
    
    # Because there's a chance that multiple files with the same name might 
    # exist in different locations we need to have a go at working out which
    # one is the one we want
    if reference_locations == False:
        return False, ief_holder
    
    reference_location = False
    best_match = {'ref': '', 'length': 0}
    for ref in reference_locations:
        lcs = longestCommonSuffix(os.path.dirname(ref), reference_file_folder)
        
        # Check that the match isn't just a trailing seperator. Then do a 
        # comparision to see which one has the longest match and use that.
        # It's still only a guess, but it's the best guess we can make.
        if not lcs == '' and not (lcs == '/' or lcs == '\\' or lcs == '\\\\'):
            if len(lcs) > best_match['length']:
                reference_location = ref
                best_match['ref'] = ref
                best_match['length'] = len(lcs)
    if reference_location == False:
        return False, ief_holder 
    
    # Find the place where the ief file and the found file meet
    ief_holder.root_folder_new = prefix = longestCommonPrefix(ief_path, reference_location)
    
    # Then split the path of the reference location with the new root.
    # This will given us only the section left after the root.
    temp = reference_location.split(prefix)[1]
    
    # Finally use temp as a mask to find the root for the old file
    # location
    ief_holder.root_folder_old = prefix_old = reference_file.split(temp)[0]

    '''Loop through the files in the ief and use prefix_old as a mask
    to find the part of the filename after the matching root folder.
    This can then be joined to the new root and we've updated the 
    file names to the new location.
    '''
    updated_paths = []
    for p in in_paths:    
        match_results = p.split(prefix_old)
        if len(match_results) > 1:
            rmatch = os.path.join(prefix, match_results[1])
            updated_paths.append(rmatch)
            ief_holder.addFile(rmatch, 'out', test_exists=True)
    
    return True, ief_holder
    
    
def longestCommonPrefix(file1, file2):
    """Find the matching parts of two filenames starting from left.
    
    Args:
        file1(str): first file name to compare.
        file2(str): second file name to compare.
    
    Return: 
        String - the file name from the left to the point where the two
            filenames no longer match. May be an empty string if the
            filenames don't share the same left-most portion..
    """
    start = 0
    while start < min(len(file1), len(file2)):
        if file1[start] != file2[start]:
            break
        start += 1
    return file1[:start]
    
    
def longestCommonSuffix(file1, file2):
    """Find the matching parts of two filenames starting from Right.
    
    Used the longestCommonPrefix() function by passing in reversed versions of
    the filepaths.
    
    Args:
        file1(str): first file name to compare.
        file2(str): second file name to compare.
        
    Return: 
        String - the file name from the right to the point where the two
            filenames no longer match. May be an empty string if the
            filenames don't share the same right-most portion..
    """
    return longestCommonPrefix(file1[::-1], file2[::-1])[::-1]

    
    
    
