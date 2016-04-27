"""
    Contains all of the variables that will be needed globally by the software.
    
    This is not a place to put things becuase you're lazy and want a shortcut!
    It shouldn't be used to break encapsulation.
    
    Items in here are needed for thing's like current version and id's that can
    easily get out of sync when harcoded into many places.
"""

__VERSION__ = 'v0.6.3-Beta'
__APPID__ = 'LogIT.0-5-Beta'
__SERVER_PATH__ = r'P:\04 IT\utils\beta\LogIT'
__DOWNLOAD_FILENAME__ = 'Logit_'
__VERSION_CHECKPATH__ = r'P:\04 IT\utils\beta\LogIT\Version_Info\versioninfo.ver'
__RELEASE_NOTES_PATH__ = r'P:\04 IT\utils\beta\LogIT\Version_Info\Release_Notes_'

__DEV_MODE__ = True


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
path_holder = {}
def setPath(key, path):
    path_holder[key] = str(path)







