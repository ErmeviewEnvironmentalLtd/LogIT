import os
import sys
sys.path.append("TMacTools-0.4.1.dev0-py2.7.egg")

from PyQt4 import QtGui

from tmactools.utils.fileloaders import fileloader as fl
from tmactools.utils.qtclasses import MyFileDialogs
from tmactools.utils import filetools as ft

class IefHolder(object):
    
    def __init__(self, ief_obj):
        self.ief_obj = ief_obj
        self.root_folder_old = ''
        self.root_folder_new = ''
        self.single_types = {'.dat': {'in': '', 'out': ''}, 
                             '.tcf': {'in': '', 'out': ''},
                             'result': {'in': '', 'out': ''}
                            }
        self.ieds_list_types = {'in': [], 'out': []}
        self.missing_types = {'.tcf': True, '.dat': True, '.ied': True, 'result': True}
        self.has_types = {'.tcf': False, '.dat': False, '.ied': False, 'result': False}
        self.selected_paths = {'.tcf': '', '.dat': '', '.ied': '', 'result': ''}
    
    
    def getUpdatedIefObj(self):
        """
        """
        p, e = os.path.splitext(self.ief_obj.path_holder.getAbsPath())
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
                self.ief_obj.event_header['Results'] = v['out']            
        
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
#         if len(extstuff) < 2 or extstuff[1] == '' or (not extstuff[1] in self.single_types.keys() and not extstuff[1] in self.ieds_list_types.keys()):
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
        """
        """
        missing = []
        for k, v in self.missing_types.iteritems():
            if self.has_types[k] == True and v == True:
                missing.append(k)
        return missing



def updateIefObjects(ief_holders):
    """
    """
    ief_objs = []
    for ief_holder in ief_holders:
        ief_objs.append(ief_holder.getUpdatedIefObj())
    
    return ief_objs


def writeUpdatedFile(ief_objs):
    """
    """
    for ief in ief_objs:
        contents = ief.getPrintableContents()
        try:
            ft.writeFile(contents, ief.path_holder.getAbsPath())
        except IOError:
            logger.error('Could nto write new ief file at:\n' + ief.path_holder.getAbsPath())
    

def resolveUnfoundPaths(ief_holders):
    """
    """
    had_to_search = {}
    for ief_holder in ief_holders:

        in_out_list = {'in': [], 'out': []}
        for k, v in ief_holder.missing_types:
            if ief_holder.has_types[k] == True and v == True:
                file_out = False
                if k in self.ief_holder.single_file_types.keys():
                    infile = ief_holder.ief_obj.single_types[k]['in']
                    filename = os.path.split(infile)[1]
                    file_out = findFile(infile, filename)
                    in_out_list['in'].append(infile)
                    in_out_list['out'].append(file_out)
                    if not file_out == False:
                        ief_holder.ief_obj.addFile(file_out, 'out', False)
                
                elif k == '.ied':
                    for ied in ief_holder.ieds_list_types:
                        filename = os.path.split(ied['in'])[1]
                        file_out = findFile(ied['in'], filename)
                        in_out_list['in'].append(infile)
                        in_out_list['out'].append(file_out)
                        if not file_out == False:
                            ief_holder.ief_obj.addFile(file_out, 'out', False)
                
                else:
                    infile = ief_holder.ief_obj.single_types['result']['in']
                    filename = os.path.split(infile)[1]
                    file_out = findFile(infile, filename)
                    in_out_list['in'].append(infile)
                    in_out_list['out'].append(file_out)
                    if not file_out == False:
                        ief_holder.ief_obj.addFile(file_out, 'out', False)
                
        had_to_search[ief_holder.ief_obj.getAbsPath()] = in_out_list
    
    return ief_holders, had_to_search

        
def findFile(start_location, file_to_find, search_folder_depth=3):
    """Walk the folder structure until you find the file or fun out of files.
    
    Args:
        start_folder(str): path to the folder to start walking from.
        extension(str): file extension to find. Stop if we find a file with
            this extension.
    
    Return:
        String - normalised absolute path of the file if found. Or False if 
            no match could be found.
    """
    # Set the number of folders to search upwards from the ief file.
    # This will be the point we start walking down the path to find
    # the reference location (the location of the reference file)
    folder_up = []
    for s in range(0, search_folder_depth):
        folder_up.append('..')
    folder_up = os.path.normpath('/'.join(folder_up))
    start_location = os.path.join(start_location, folder_up)

    for root, dir, files in os.walk(start_location):
        for f in files:
            splitted = os.path.split(f)
            if len(splitted) > 1 and splitted[1].lower() == file_to_find.lower():
                return os.path.normpath(os.path.join(root, f))
    
    return False


def autoResolveIefs(iefs):
    """
    """
    ief_holders = []
    for ief in iefs:
        success, new_holder = autoResolvePath(ief)
        if success:
            ief_holders.append(new_holder)
        else:
            return False, ief_holders
    
    return True, ief_holders
    
    
def autoResolvePath(ief_path, search_folder_depth=3):
    """Change the file name in an ief to match it's new location.
    """
    loader = fl.FileLoader()
    ief_obj = loader.loadFile(ief_path)
    ief_holder = IefHolder(ief_obj)
    
    # Get the location of the ief file we just loaded
    cur_ief_location = os.path.split(ief_path)[0]
#     print '\n\n\n\nIef location: ' + cur_ief_location
    
    # Get the dat and results paths from ief object
    ief_files_refs = ief_obj.getFilePaths()[0]
    ief_datafile = ief_files_refs['datafile']
    ief_holder.addFile(ief_datafile, 'in', test_exists=False)

    # Don't get the placeholder filename for the results
    ief_resultsfile = os.path.split(ief_files_refs['results'])[0]
    ief_holder.addFile(ief_resultsfile, 'in', test_exists=False)
    in_paths = [ief_datafile, ief_resultsfile]
    
    # If there's a 2d file then set it as the reference file. The reference
    # file is the one we use to define the most 'upstream' folder. I.e. the
    # root of all the model files. Use 2d if it's available because it will
    # most likely define a more upstream folder location.
    if 'twodfile' in ief_files_refs.keys():
        reference_file = ief_files_refs['twodfile']
        ief_holder.addFile(reference_file, 'in', test_exists=False)
        in_paths.append(ief_files_refs['twodfile'])
    else:
        reference_file = ief_files_refs['datafile']
    ref_ext = os.path.splitext(reference_file)[1]

    # Get the folder of the reference file without the file name
    reference_file_folder, reference_file_file = os.path.split(reference_file)
    reference_file_folder = os.path.normpath(reference_file_folder)
    reference_file_file = os.path.normpath(reference_file_file)
    
    # Walk from given folder point upstream until we find the
    # reference file.
    reference_location = findFile(ief_path, reference_file_file, search_folder_depth) #ref_ext)
    if reference_location == False:
#         print '\n\nError - Unable to find reference file'
        return False, ief_holders
    
    # Find the place where the ief file and the found file meet
    ief_holder.root_folder_new = prefix = longestCommonPrefix(ief_path, reference_location)
    
    # Then split the path of the reference location with the new root.
    # This will given us only the section left after the root.
    temp = reference_location.split(prefix)[1]
    
    # Finally use temp as a mask to find the root for the old file
    # location
    ief_holder.root_folder_old = prefix_old = reference_file.split(temp)[0]

    # Loop through the files in the ief and use prefix_old as a mask
    # to find the part of the filename after the matching root folder.
    # This can then be joined to the new root and we've updated the 
    # file names to the new location.
    updated_paths = []
    for p in in_paths:    
        match_results = p.split(prefix_old)
        if len(match_results) > 1:
            rmatch = os.path.join(prefix, match_results[1])
#             print '\nFound Match: ' + str(rmatch)
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
    
    Args:
        file1(str): first file name to compare.
        file2(str): second file name to compare.
        
    Return: 
        String - the file name from the right to the point where the two
            filenames no longer match. May be an empty string if the
            filenames don't share the same right-most portion..
    """
    return longestCommonPrefix(file1[::-1], file2[::-1])[::-1]

    
    
    
