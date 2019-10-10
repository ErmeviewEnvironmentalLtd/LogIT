"""
  Name: prep_release.py
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
 
 
  Module:          prep_release.py
  Date:            04/02/2016
  Author:          Duncan Runnacles
  Version:   0.1
  
  Summary:
    Prepares files for release. 
    
    Updates any version information in the software, which should be identified
    with a placeholder string. Updates the READ_ME.txt file release section 
    with the content in a release notes file. Copies all files to a given
    release directory.
 
  UPDATES:
      
     
  TODO:
     
"""

import os
import sys
import shutil
import json
import zipfile

# Load local configuration file for release setup
release_config = None
try:
    release_config = json.load(open('./release_configuration.json', 'r'))
except:
    print('UNABLE TO LOAD release_configuration.json FILE')
    sys.exit()

#
# - PREP CONFIG -
#
INPUT_DIR = os.getcwd()
VERSION = release_config['Version']
SYSTEM_BUILD = release_config['System_Build']
DIST_DIR = os.path.abspath(release_config['Dist_Folder'])
OUTPUT_DIR = os.path.join(DIST_DIR, 'src')
COPY_FOLDER = os.path.join(INPUT_DIR, 'src')

VERSION_PLACEHOLDER = '~VERSION~'
VERSION_FILES = [
    os.path.join(INPUT_DIR, 'src', 'logit', 'LogIT_UI_qt5.py'),
    os.path.join(INPUT_DIR, 'src', 'logit', 'LogIT_UI_qt5.ui')
]
                 
README_FILE = os.path.join(INPUT_DIR, 'src', 'READ_ME.txt')
RELEASE_INFO = os.path.join(INPUT_DIR, 'src', 'Release_Notes.txt')

SETTINGS_LINE_RELEASE = '__DEV_MODE__ = False'
SETTINGS_LINE_DEV = '__DEV_MODE__ = True'
SETTINGS_FILE = os.path.join(INPUT_DIR, 'src', 'logit', 'globalsettings.py')


#
# - BUILD CONFIG -
#
# If True the executable will be built into a smaller single file.
# If False it will include a separate folder with dependencies, but be
# a lot bigger (> 100MB bigger)
BUILD_ONEFILE = True

# The activate_this.py file in the virtual env. This should be included in 
# your virtual environment. 
# On Windows it will be something like:
# c:/some/path/your-env-name/Scripts/activate_this.py
# On linux something like:
# /some/path/your-env-name/bin/activate_this.py
# If you're not using a virtual env set activate_this_file = None
activate_this_file = os.path.join(
    INPUT_DIR, 'env', 'Scripts', 'activate_this.py'
)
# Python executable in the environment containing pyinstaller
ENV_PATH = os.path.join(INPUT_DIR, 'env')
PYTHON_EXE = os.path.join(
    ENV_PATH, 'Scripts', 'python.exe'
)
PYINSTALLER_PATH = os.path.join(
    ENV_PATH, 'Scripts', 'pyinstaller.exe'
)
PROJECT_NAME = 'LogIT'

#
# - EXPORT CONFIG -
#
# Zip up and prep for exporting config
BINARY_DIR = os.path.join(DIST_DIR, 'dist')
#TEMPLATE_DIR = os.path.join(INPUT_DIR, 'templates')
SRC_DIR_IN = os.path.join(DIST_DIR, 'src', 'logit')
EXTRAS_DIR_IN = os.path.join(DIST_DIR, 'src')

RELEASE_NAME = 'logIT_' + VERSION + '_' + SYSTEM_BUILD
FINAL_OUTPUT_DIR = os.path.join(DIST_DIR, RELEASE_NAME)
SRC_DIR_OUT = os.path.join(FINAL_OUTPUT_DIR, 'src')
TOOL_SETTINGS_FILES = [
    os.path.join(SRC_DIR_OUT, 'settings.json'),
    os.path.join(FINAL_OUTPUT_DIR, 'settings.json'),
]
ZIP_LOG = FINAL_OUTPUT_DIR + '.zip'


def setupOutputDir(dir):
    """Create the folder for the output directory if it doesn't exist
    """
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)#, 0777)
    except IOError:
        print('Cannot creat OUTPUT_DIR at: ' + dir)
        return False
    return True


def cleanDirPrep(dir):
    """Deletes the contents of the output directory.
    """
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    
def inplace_change(filename, old_string, new_string):
    """Perform a string replace on all matching strings within the file.
    """
    found = False
    s = open(filename).read()
    if old_string in s:
        #print 'Changing "{old_string}" to "{new_string}"'.format(**locals())
        found = True
        s = s.replace(old_string, new_string)
        f = open(filename, 'w')
        f.write(s)
        f.flush()
        f.close()
    else:
        found = False
    return found


def findInFile(filename, the_string):
    """Check if string exists in file.
    """
    found = False
    s=open(filename).read()
    if the_string in s:
        found = True
    
    return found


def updateGlobalSettingsVersion():
    """Updates the version code in globalsettings.py.
     
    This can't use a place holder because it's needed when developing, so 
    must contain a value at all times.
    """
    new_version = "__VERSION__ = '" + VERSION + "'\n"
    settings_new = SETTINGS_FILE + '_new'
    with open(SETTINGS_FILE, 'r') as s:
        with open(settings_new, 'w') as n:
            for line in s:
                n.write(new_version if '__VERSION__' in line else line)
    
    os.remove(SETTINGS_FILE)
    os.rename(settings_new, SETTINGS_FILE)
    
    
def updateVersion(old, new):
    """Update the version placeholder string for all files in the list.
    
    Add files to VERSION_FILES to be included in update.
    """
    for vf in VERSION_FILES:
        found = inplace_change(vf, old, new)
        if not found:
            print('Could not find placeholder (%s) in file:\n%s' % (old, vf))
        

def removeReadmeReleaseNotes():
    """Deletes release notes for this version if they already exist.
    
    This is used done so that any changes will be included.
    """
    writing = True
    README_FILE_OUT = README_FILE + '.bak'
    try:
        with open(README_FILE) as f:
            with open(README_FILE_OUT, 'w') as out:
                for line in f:
                    if writing:
                        if VERSION in line and not 'Version:' in line:
                            writing = False
                            buffer = [line]
                        else:
                            out.write(line)
                    elif "##~##" in line:
                        writing = True
                        out.write(line)
                    else:
                        buffer.append(line)
                else:
                    if not writing:
                        #There wasn't a closing line, so write buffer contents
                        out.writelines(buffer)
    except:
        print('\t-> Failed to remove outdated release notes - exit now!')
        sys.exit()
        
    os.remove(README_FILE)
    os.rename(README_FILE_OUT, README_FILE)
                
                
def updateReadme():
    """Update the READ_ME.txt file with the version number and release notes.
    """
    found_existing = findInFile(README_FILE, VERSION)
    if found_existing:
        removeReadmeReleaseNotes()
    
    found = inplace_change(README_FILE, VERSION_PLACEHOLDER, VERSION)
    
    updates_in = open(RELEASE_INFO).readlines()
    updates_out = []
    updates_out.append(VERSION + ':\n')
    for u in updates_in:
        updates_out.append('    ' + u)
    updates_out.append('\n\n##~##')
    updates_out = ''.join(updates_out)
    
    found = inplace_change(README_FILE, '##~##', updates_out)
    if not found:
        print('Could not find placeholder (%s) to update READ_ME file' % (VERSION_PLACEHOLDER))
    
    
def updateDevmode(make_dev=True):
    """Set __DEV_MODE__ variables to either True or False.
    """
    if not SETTINGS_FILE is None:
        found1 = findInFile(SETTINGS_FILE, SETTINGS_LINE_DEV)
        found2 = findInFile(SETTINGS_FILE, SETTINGS_LINE_RELEASE)
        if found1: 
            replace_val = SETTINGS_LINE_DEV
        else:
            replace_val = SETTINGS_LINE_RELEASE
        
        if make_dev:
            found = inplace_change(SETTINGS_FILE, replace_val, SETTINGS_LINE_DEV)
        else:
            found = inplace_change(SETTINGS_FILE, replace_val, SETTINGS_LINE_RELEASE)
        
        if not found:
            print('Unable to update __DEV_MODE__ in settings file')
    

def copyTree(src, dst, symlinks=False, ignore=None):
    """Copy the contents from one folder to another.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            
def copyExtrasPrep(output_dst):
    """Copy any extra files like READ_ME's.
    """
    shutil.copy(README_FILE, output_dst)
    shutil.copy(RELEASE_INFO, output_dst)


def resetReadmeVersion():
    """Reset the Version: string at top of READ_ME to placeholder value.
    
    Can't use global replace because that will affect the version string in
    the updates section.
    """
    found = inplace_change(README_FILE, 'Version: ' + VERSION, 'Version: ' + VERSION_PLACEHOLDER)
    if not found:
        print('Unable to update VERSION in READ_ME file')


def cleanDirExport(dir):
    """Deletes the contents of the output directory.
    """
    if not os.path.exists(dir):
        return
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    
def copyTree(src, dst, symlinks=False, ignore=None):
    """Copy the contents from one folder to another.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            

def copyExtrasExport():
    """Copy any extra files like READ_ME's.
    """
    shutil.copy(os.path.join(EXTRAS_DIR_IN, 'READ_ME.txt'), FINAL_OUTPUT_DIR)
    shutil.copy(os.path.join(EXTRAS_DIR_IN, 'Release_Notes.txt'), FINAL_OUTPUT_DIR)


def zipupRelease():
    """Zip up the release folder reading for exporting.
    """
    # Remove any existing zip file
    if os.path.exists(ZIP_LOG):
        try:
            os.remove(ZIP_LOG)
            print('\t-> Deleted existing zipped release file.')
        except:
            print('\t-> Unable to delete existing zipped release file.')
    
    # Zip up release folder
    zipobj = zipfile.ZipFile(os.path.join(FINAL_OUTPUT_DIR + '.zip'), 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(FINAL_OUTPUT_DIR) + 1
    for base, dirs, files in os.walk(FINAL_OUTPUT_DIR):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])

    print('\t-> Release folder zipped.')
    

def deleteExistingLogs():
    """Delete any log folders that may exist before sending out."""
    try:
        shutil.rmtree(os.path.join(FINAL_OUTPUT_DIR, 'logs'))
    except:
        print('\t-> No release folder logs folder found')
    try:
        shutil.rmtree(os.path.join(FINAL_OUTPUT_DIR, 'LogIT', 'logs'))
    except:
        print('\t-> No binary folder logs folder found')
    try:
        os.remove(os.path.join(FINAL_OUTPUT_DIR, 'src', 'logs.zip'))
    except:
        print('\t-> No logs.zip file found in src')
    try:
        shutil.rmtree(os.path.join(FINAL_OUTPUT_DIR, 'src', 'logs'))
    except:
        print('\t No logs folder found in src')
    try:
        shutil.rmtree(os.path.join(FINAL_OUTPUT_DIR, 'local_regression_tests'))
    except:
        print('\t-> Could not remove regression test folder')


def deleteBuildFiles():
    try:
        shutil.rmtree(os.path.join(DIST_DIR, 'dist'))
        shutil.rmtree(os.path.join(DIST_DIR, 'build'))
        shutil.rmtree(os.path.join(DIST_DIR, 'src'))
    except:
        print('\nFailed to delete build file folders')
    
    
def prepRelease():

    print('Setting up output dir if required...')
    setupOutputDir(OUTPUT_DIR)
    
    print('Cleaning output directory...')
    cleanDirPrep(OUTPUT_DIR)
    
    print('Updating version info in files...')
    updateVersion(VERSION_PLACEHOLDER, VERSION); updateGlobalSettingsVersion()
    
    print('Updating __DEV_MODE__ ...')
    updateDevmode(False)
    
    print('Updating READ_ME file...')
    updateReadme()
    
    print('Copying files across...')
    copyTree(COPY_FOLDER, OUTPUT_DIR)
    
    print('Copying any extra files across...')
    copyExtrasPrep(OUTPUT_DIR)
    
    print('Resetting VERSION...')
    updateVersion(VERSION, VERSION_PLACEHOLDER)
    
    print('Resetting __DEV_MODE__ ...')
    updateDevmode(True)
    
    print('Resetting READ_ME version...')
    resetReadmeVersion()
    
    print('\nRelease preparation complete :)')
    
    
def buildExe():
    """"""
    print('\nBuilding executable with PyInstaller...')
    exec(open(activate_this_file).read(), dict(__file__=activate_this_file))
    #MAKESPEC_CMD = """%s %s\Makespec.py -X -n %s -F %s""" % (PYTHON_EXECUTABLE, PYINSTALLER_PATH, PROJECT_NAME, PROJECT_MAIN_SCRIPT)
    
    # Creates an executable with required packages in a separate folder (big ~ 170MB)
    spec_file = os.path.join(DIST_DIR, '..', 'LogIT.spec')
    # Creates a standalone executable without additional folder (much smaller ~50MB)
    onefile_spec = os.path.join(DIST_DIR, '..', 'LogIT_Onefile.spec')
    dist_dir = os.path.join(DIST_DIR, 'dist')
    build_dir = os.path.join(DIST_DIR, 'build')
    
    spec = onefile_spec
    if BUILD_ONEFILE:
        spec = spec_file
    BUILD_CMD = '"{0} --noconfirm --log-level=ERROR --onefile --workpath={1} --distpath={2} {3}"'.format(
        PYINSTALLER_PATH, build_dir, dist_dir, spec 
    )

#     os.system(MAKESPEC_CMD)
    if os.system(BUILD_CMD):
        raise RuntimeError('program {} failed!'.format(BUILD_CMD))
#     os.system(BUILD_CMD)
    print('Exe build complete.\n')
    
    
def export():
    print('Setting up SRC output dir if required...')
    setupOutputDir(FINAL_OUTPUT_DIR)
    setupOutputDir(SRC_DIR_OUT)
    
    print('Cleaning SRC output directory...')
    cleanDirExport(FINAL_OUTPUT_DIR)
    cleanDirExport(SRC_DIR_OUT)

    print('Copying executable files...')
    copyTree(BINARY_DIR, FINAL_OUTPUT_DIR)
        
    print('Copying source files...')
    try:
        os.mkdir(SRC_DIR_OUT)
    except:
        print('\t-> Failed to make src directory. Exiting now.')
        sys.exit()
    copyTree(SRC_DIR_IN, SRC_DIR_OUT)

    print('Copying extra files...')
    copyExtrasExport()
    
    print('Deleting logs if found...')
    deleteExistingLogs()
        
    print('Deleting settings if found...')
    for tsf in TOOL_SETTINGS_FILES:
        try:
            os.remove(tsf)
        except:
            pass
    
    print('Deleting unwanted second .exe...')
    try:
        os.remove(os.path.join(FINAL_OUTPUT_DIR, 'LogIT', 'LogIT.exe'))
    except:
        print('\t-> Failed to delete unwanted .exe file')
    
    print('Zipping up release...')
    zipupRelease()
    
    if BUILD_ONEFILE:
        print('Removing unwanted dependecy folder...')
        try:
            shutil.rmtree(os.path.join(FINAL_OUTPUT_DIR, 'LogIT'))
        except:
            print('Failed to remove unwanted dependency folder')



if __name__ == '__main__':
    args = sys.argv
    prepRelease()
    buildExe()
    export()
    
    if len(args) > 1 and args[1] == '--del-build-files':
        deleteBuildFiles()
    print("\n\nRELEASE COMPLETE")