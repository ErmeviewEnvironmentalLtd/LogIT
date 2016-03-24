import sys
sys.path.append("TMacTools-0.4.1.dev0-py2.7.egg")

import os

from tmactools.utils.fileloaders import fileloader as fl


def resolveUnfoundPaths(found_folders):
    """
    """
    for key, folder in found_folders:
        if folder == '': continue
        
        

def resolveIefs(iefs):
    """
    """
    not_found = []
    for ief in iefs:
        Success, found, missing, root_folder = resolvePaths(ief)
        if not success:
            not_found.extend(missing)
    
    missing_types = {'.TCF': False, '.DAT': False, '.IED': False, 'Result': False}
    output_message = ['The following file types could not be found\nPlease use the following dialogs to locate their folders.']
    if missing_files:
        for m in missing_files:
            extstuff = os.path.splitext(m)
            if len(extstuff) < 2:
                missing_types['Result'] = True
                output_message.append('results')
            else:
                missing_types[extstuff.upper()] = m
                output_message.append(m)
    
    if len(output_message) < 2: output_message = ['Ief files successfully updated']

    return missing_types, folder
    
    
    
def resolvePath(ief_path, search_folder_depth=3):
    """Change the file name in an ief to match it's new location.
    """
#     search_folder_depth = 3
#     new_dat_location = r'C:\Users\duncan.runnacles.KEN\Desktop\Temp\path_resolver\model\isis\dat\kennford_1%AEP_FINAL_v1.17\kennford_1%AEP_FINAL_v1.17.DAT'
#     ief_path = r'C:\Users\duncan.runnacles.KEN\Desktop\Temp\path_resolver\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
    
    loader = fl.FileLoader()
    ief = loader.loadFile(ief_path)
    
    # Get the location of the ief file we just loaded
    folder = cur_ief_location = os.path.split(ief_path)[0]
#     print '\n\n\n\nIef location: ' + cur_ief_location
    
    # Get the dat and results paths from ief object
    ief_files_refs = ief.getFilePaths()[0]
    ief_datafile = ief_files_refs['datafile']
    
    # Don't get the placeholder filename for the results
    ief_resultsfile = os.path.split(ief_files_refs['results'])[0]
    in_paths = [ief_datafile, ief_resultsfile]
    
    # If there's a 2d file then set it as the reference file. The reference
    # file is the one we use to define the most 'upstream' folder. I.e. the
    # root of all the model files. Use 2d if it's available because it will
    # most likely define a more upstream folder location.
    if 'twodfile' in ief_files_refs.keys():
        reference_file = ief_files_refs['twodfile']
        in_paths.append(ief_files_refs['twodfile'])
    else:
        reference_file = ief_files_refs['datafile']
    ref_ext = os.path.splitext(reference_file)[1]

    # Get the folder of the reference file without the file name
    reference_file_folder = os.path.normpath(os.path.split(reference_file)[0])
    
    # Set the number of folders to search upwards from the ief file.
    # This will be the point we start walking down the path to find
    # the reference location (the location of the reference file)
    folder_up = []
    for s in range(0, search_folder_depth):
        folder_up.append('..')
    folder_up = os.path.normpath('/'.join(folder_up))
    folder_up = os.path.join(ief_path, folder_up)
#     print '\nFolder up: ' + folder_up
    
    # Walk from given folder point upstream until we find the
    # reference file.
    reference_location = findFile(folder_up, ref_ext)
    if reference_location == False:
#         print '\n\nError - Unable to find reference file'
        return False, [], [], folder
    
    # Find the place where the ief file and the found file meet
    folder = prefix = longestCommonPrefix(ief_path, reference_location)
    
    # Then split the path of the reference location with the new root.
    # This will given us only the section left after the root.
    temp = reference_location.split(prefix)[1]
    
    # Finally use temp as a mask to find the root for the old file
    # location
    prefix_old = reference_file.split(temp)[0]

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
        else:
            return False, [], []
#             print 'No match found'
    
#     print '\n\nUpdated Paths:'
    not_found = []
    found = []
    for match in updated_paths:
        if not os.path.exists(match) and not os.path.isdir(match):
            not_found.append(match)
#             print 'File does not exist! - ' + match
        else:
            found.append(match)
#             print match
    
    return True, found, not_found, folder
    
    
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

    
def findFile(start_folder, extension):
    """Walk the folder structure until you find the file or fun out of files.
    
    Args:
        start_folder(str): path to the folder to start walking from.
        extension(str): file extension to find. Stop if we find a file with
            this extension.
    
    Return:
        String - normalised absolute path of the file if found. Or False if 
            no match could be found.
    """
    for root, dir, files in os.walk(start_folder):
        for f in files:
            extstuff = os.path.splitext(f)
            if len(extstuff) > 1 and extstuff[1].upper() == extension.upper():
                return os.path.normpath(os.path.join(root, f))
    
    return False
    
    
