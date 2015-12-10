'''
###############################################################################
#    
# Name: LogIT (Logger for Isis and Tuflow) 
# Author: Duncan Runnacles
# Copyright: (C) 2014 Duncan Runnacles
# email: duncan.runnacles@thomasmackay.co.uk
# License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
# Module:  LogClasses.py 
# Date:  07/12/2015
# Author:  Duncan Runnacles
# Version: 1.0
# 
# Summary:
#    Onjects and functions for dealing with the logs data.
#
# UPDATES:
#   
#
# TODO:
#
###############################################################################
'''


import logging
logger = logging.getLogger(__name__)

class AllLogs(object):
    '''Container class for all of the SubLog objects.
    '''
    
    
    SINGLE_FILE = ['RUN', 'DAT']
    
    def __init__(self, log_pages):
        '''Create new SubLog and set multi_file.
        '''
        self.editing_allowed = ['COMMENTS', 'MODELLER', 'SETUP', 'DESCRIPTION',
                           'EVENT_NAME', 'EVENT_DURATION', 'ISIS_BUILD',
                           'TUFLOW_BUILD', 'AMENDMENTS']
        self.export_tables = ['RUN', 'TCF', 'ECF', 'TGC', 'TBC', 'DAT', 'BC_DBASE']

        self.log_pages = {}        
        for key, page in log_pages.iteritems():
            if key in AllLogs.SINGLE_FILE:
                self.log_pages[key] = SubLog(key, page, False)
            else:
                self.log_pages[key] = SubLog(key, page, True)
    
    
    def getLogEntryContents(self, key, index=None):
        '''Get the log entry at the given key and index.
        @param key: the key to the SubLog entry.
        @param index=None: the index in the contents list to return.
        '''
        if index == None:
            return self.log_pages[key].contents
        else:
            return self.log_pages[key].contents[index]
    
    def getLogDictionary(self):
        '''Return all logs in class as a dictionary.
        '''
        out_log = {}
        for page in self.log_pages.values():
            # DEBUG - have to convert back from list at the moment
            if page.name in AllLogs.SINGLE_FILE:
                if not len(page.contents) < 1:
                    page.contents = page.contents[0]
            out_log[page.name] = page.contents
        
        return out_log
    
    def getUpdateCheck(self):
        '''Return dictionary containing update status.
        Update status is a boolean flag indicating whether a log page should
        be updated or not.
        '''
        out_check = {}
        for page in self.log_pages.values():
            out_check[page.name] = page.update_check
        
        return out_check
        

class SubLog(object):
    '''Log page objects.
    E.g. RUN, TGC, etc.
    '''
    
    def __init__(self, name, sub_page, multi_file):
        '''Set vars and make sure everything is in the format needed.
        '''
        self.name = name
        self.multi_file = multi_file
        self.has_contents = self._checkHasContents(sub_page)
        sub_page = self._checkIsList(sub_page)
        self.contents = sub_page
        self.update_check = False
        #self.update_check = self._createUpdateCheck(sub_page)
        self.subfile_name = None
        if multi_file: self.subfile_name = name + '_FILES'
    
    
    def _checkIsList(self, sub_page):
        '''Checks if given page is in a list and puts it in one if not.
        
        Some pages like RUN and DAT can only have one entry, while the others
        may have many. Originally the others were put in a list and RUN & DAT
        weren't. This is a design fault and this method can be removed once 
        it is dealt with throughout the codebase.
        '''
        if not isinstance(sub_page, list):
            sub_page = [sub_page]
        return sub_page
    
    def _checkHasContents(self, contents):
        '''Checks the status of the page contents.
        
        If the contents are set to a default value this will return False.
        This should also be possible to clean up by ensuring only a single
        default value is used throughout the codebase.
        '''
        if not self.name == 'RUN':
            if self.multi_file:
                if contents[0] == 'None' or contents[0] == False or contents[0] == None:
                    return False
                elif contents[0][self.name] == 'None':
                    return False
            else:
                if contents == 'None' or contents == False or contents == None:
                    return False
                elif contents[self.name] == 'None':
                    return False

        return True
    
    
    def updateValues(self, row, index):
        '''
        '''
        self.contents[index] = row
    
    
    def bracketFiles(self, index, key, files=None):
        '''Encloses all of the files, under a certain key, in brackets.
        If not files==None a new key will be created and those files will be
        enclosed in brackets.
        '''
        if not files == None: self.contents[index][key] = files
        self.contents[index][key] = "[" + ", ".join(self.contents[index][key]) + "]"
    
    def deleteItem(self, index):
        '''Deletes an item (i.e. a row) from the contents.
        '''
        del self.contents[index]
        
        

