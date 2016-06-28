"""
###############################################################################
    
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


 Module:          AWidget.py 
 Date:            26/04/2016
 Author:          Duncan Runnacles
 Since-Version:   0.7
 
 Summary:
     Abstract class that provides an interface for all widgets used by LogIt.
     These will be called by the MainGui class at startup and added to the
     main QTabWidget.
     This class provides a range of convenience methods for launching 
     QMessagebox's, loading and saving data to the cache etc.
     There are also some methods such a load/save settings and loadto/savefrom
     cache that need to be implemented for the main gui to function properly.
     All widgets MUST implement this interface, but the settings and cache
     methods can be overridden is required.

 UPDATES:    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)


import cPickle
import os


class ATool(object):
    
    def __init__(self, tool_name, cwd, create_data_dir=True):
        self.cur_location = cwd
        self.settings = self.getSettingsAttrs()
        self.tool_name = str(tool_name)
        self.data_dir = None
        if create_data_dir:
            self.createDataDir()
    
    
    def createDataDir(self): 
        """Sets up a data folder to store caches etc in."""
        
        # Create a data cache folder if one doesn't already exist
        if not os.path.exists(os.path.join(self.cur_location, 'data')):
            try:
                os.mkdir(os.path.join(self.cur_location, 'data'))
            except Exception, err:
                logger.warning('Could not create data directory')
                logger.exception(err)
        self.data_dir = os.path.join(self.cur_location, 'data', str(self.tool_name))
        if not os.path.exists(self.data_dir):
            try:
                os.mkdir(self.data_dir)
            except Exception, err:
                logger.warning('Could not create tool data directory:' + self.data_dir)
                logger.exception(err)
        
    
    def getSettingsAttrs(self):
        """Get the attributes to include in this class' ToolSettings.
        
        Note:
            This should be overriden by the concrete class. If it isn't the
            ToolSettings will contain only the tool_name and guid.
        
        Return:
            dict - containing {variable name: default} for all member variables
                added to the ToolSettings.
        """
        return {}
        
        
    def loadSettings(self, settings):
        """Updates the settings for this instance with those provided.
        
        Any variables in the given settings dict that don't/no longer exist in 
        the current setup will be ignored.
        
        Args:
            settings(ToolSettings): containing member variable states to 
                update.
        """
        for key, val in self.settings.iteritems():
            if key in settings.keys():
                self.settings[key] = settings[key]
        

    def saveSettings(self):
        """Return the ToolSettings instance to the caller.
        
        By default it literally just return the current state of the 
        ToolSettings. If any other updates should be made before this happend
        this method should be overriden.
        """
        return self.settings
    

    def activate(self):
        """Will be called by the MainGui class whenever the widget is activated.
        
        By default this method does nothing. If anything should be done when
        a widget it activated this method should be overridden. This might
        include loading some data to the cache, resetting inputs or suchlike.
        """
        pass
    

    def deactivate(self):
        """Will be called by the MainGui class whenever the widget is deactivated.
        
        By default this method does nothing. If anything should be done when
        a widget it deactivated this method should be overridden. This might
        include saving some data to the cache or suchlike to make sure that
        the widget isn't hogging lots of memory when not in use.
        """
        pass
    
    
    def _saveToCache(self, cachefile, path):
        """Uses pickle to store the state of the given object."""
        try:
            with open(path, "wb") as p:
                cPickle.dump(cachefile, p)
        except IOError:
            logger.error('Unable to cache file:' + path)
            raise

    
    def _loadFromCache(self, cachefile_path):
        """Uses pickle to load the state of a pickled object from file."""
        try:
            # Load the settings dictionary
            cache = cPickle.load(open(cachefile_path, "rb"))
            return cache
        except IOError:
            logger.error('Unable to load cache file: ' + cachefile_path)
            raise
    
    

        
        
    