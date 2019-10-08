"""
    Contains all of the variables that will be needed globally by the software.
    
    This is not a place to put things becuase you're lazy and want a shortcut!
    It shouldn't be used to break encapsulation.
    
    Items in here are needed for thing's like current version and id's that can
    easily get out of sync when harcoded into many places.
"""

__VERSION__ = 'v2.0.0'
__APPID__ = 'LogIT.1-0-Beta'
__SERVER_PATH__ = r'P:\04 IT\utils\beta\LogIT'
__DOWNLOAD_FILENAME__ = 'Logit_'
__VERSION_CHECKPATH__ = r'P:\04 IT\utils\beta\LogIT\Version_Info\v1\versioninfo.ver'
__RELEASE_NOTES_PATH__ = r'P:\04 IT\utils\beta\LogIT\Version_Info\v1\Release_Notes_'

__DEV_MODE__ = True
__TEST_MODE__ = False


'''
    Global variables that need to be shared by all widgets.
    Having these here just saves a lot of code and makes it simple for all
    widgets to interact with the same file locations.
    
    Standard ones to use are:
        - model
        - output
        - log
    
    But you can put anything in there.
'''
import os

path_holder = {}
def setPath(key, path):
    """Sets a path and converts to str in case of QString."""
    path_holder[key] = str(path)
    path_holder['last_path'] = str(path)

def getPath(key):
    """Check if path variable sets and checks it exists if requested.
    
    Args:
        key(str): key to the path variable in path_holder.
    
    Return:
        tuple(str, bool): path and exist status. Path can be False if the key
            is not found in path_holder.
    """
    path = False
    exists = False
    if key in path_holder.keys():
        path = path_holder[key]
    if not path == False:
        exists = os.path.exists(path)
    return path, exists







