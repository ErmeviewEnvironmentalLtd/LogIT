'''
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


 Module:           LogClasses.py 
 Date:             07/12/2015
 Author:           Duncan Runnacles
 Since-Version:    0.3.1
 
 Summary:
    Objects and functions for dealing with the logs data. All log information
    is stored in these classes when loaded. They provide convenience functions
    for easily access the data and converting it.

 UPDATES:
     DR - 08/09/2016:
       Complete re-write and simplification of the AllLogs class.
       Includes removal of SubLogs.

 TODO:

###############################################################################
'''


import logging
logger = logging.getLogger(__name__)

import hashlib

EDITING_ALLOWED = ['COMMENTS', 'MODELLER', 'SETUP', 'DESCRIPTION',
                   'EVENT_NAME', 'EVENT_DURATION', 'ISIS_BUILD',
                   'TUFLOW_BUILD', 'AMENDMENTS', 'RUN_OPTIONS', 'MB',
                   'RUN_STATUS']
"""AllLogs keys for which value editing is permitted."""

class AllLogs(object):
    """Holder for the log data when loaded.
    
    Used by the LogBuilder module to store the data and return it to the
    calling class.
    
    Contains methods for storing, accessing, and updating log data.
    """
    
    TYPES = ['RUN', 'MODEL', 'DAT', 'SUBFILE']
    
    def __init__(self, run_filename, tcf_dir='', ief_dir=''):
        self.editing_allowed = EDITING_ALLOWED
        self.tcf_dir = tcf_dir
        self.ief_dir = ief_dir
        self.run_filename = run_filename
        self.run_hash = None
        self.run = None
        self.dat = None
        self.models = []
        
    
    def addLogEntry(self, entry, type=None):
        """Add a new entry to the log.
        
        Args:
            entry(str): LOG, 'DAT', or 'MODEL'
        """
        for e in entry:
            if e['TYPE'] == 'RUN':
                self.run = e
                self._buildRunName()
            elif e['TYPE'] == 'DAT':
                if e['NAME'].strip() != '':
                    self.dat = e
            else:
                self.models.append(e)
                self.models[-1]['INDEX'] = len(self.models) - 1
    
    def _buildRunName(self):
        """Creates a run hash str for this run.
        
        Creates a unique hash code for the run. This is unique to a set of run
        variables NOT unique everytime. It is used to check that the run 
        doesn't already exist in the database.
        
        The hash uses a salt made up of:  
            tcf name + ief name + run options
            
        This combination of variables should not exist in two different runs.
        """
        rn = []
        if not self.run['TCF'].strip() == '':
            rn.append(self.run['TCF'].strip())
        if not self.run['IEF'].strip() == '':
            rn.append(self.run['IEF'].strip())
        if not self.run['RUN_OPTIONS'].strip() == '':
            rn.append(self.run['RUN_OPTIONS'].strip())
        
        self.run_hash = hashlib.sha1(';'.join(rn)).hexdigest()
    
    
    def updateLogEntry(self, entry, values, index=None):
        """Update the values in an existing log entry.
        
        Only values that can be edited will be updated.
        
        Args:
            entry(str): RUN, DAT or MODEL.
            values(dict): key, value pairs for those needing updating.
        """        
        if entry == 'RUN':
            for k, v in values.items():
                if k in self.editing_allowed:
                    self.run[k] = v
            
        elif entry == 'DAT':
            for k, v in values.items():
                if k in self.editing_allowed:
                    self.dat[k] = v
            
        else:
            for k, v in values.items():
                if k in self.editing_allowed:
                    self.models[int(values['INDEX'])][k] = v
            
    
    

