'''
###############################################################################
#    
# Name: LogIT (Logger for Isis and Tuflow) 
# Version: 0.2-Beta
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
# Module:  Controller.py 
# Date:  16/11/2014
# Author:  Duncan Runnacles
# Version:  1.0
# 
# Summary:
#    Controller functions for the GUI. Code that is not directly responsible 
#    for updating or retrieving from the GUI is included in this module in
#    order to separate it from the application library.
#
# UPDATES:
#
# TODO:
#
###############################################################################
'''
import os

# Local modules
import DatabaseFunctions

import logging
logger = logging.getLogger(__name__)

def logEntryUpdates(conn, log_pages):
    '''Update the database with the current status of the log_pages dictionary.
    
    @param conn: an open database connection.
    @param log_pages: dictionary containing the the data to enter into the 
           database under the database table names.
    '''
    update_check = {'TGC': log_pages['RUN']['TGC'], 
                    'TBC': log_pages['RUN']['TBC'], 
                    'DAT': log_pages['RUN']['DAT'], 
                    'BC_DBASE': log_pages['RUN']['BC_DBASE']} 
    
    for u in update_check:
            
        # We can have a log page set to None so skip it if we find one.
        if log_pages[u] == None: 
            update_check[u] = False
            continue
        
        # We need to maximum id so that we can increment by 1 and put it into
        # the output table in the GUI.
        max_id = DatabaseFunctions.getMaxIDFromTable(conn, u) + 1
        
        # Need to deal with these separately because they have quite
        # specific behaviour with files etc
        if u == 'TGC' or u == 'TBC':
            update_check[u] = True
            
            # These hold a list of different model files so cycle through them
            for i, f in enumerate(log_pages[u], 0):
                table_name = u + '_FILES'

                # The FILES entry is a dictionary that uses the file
                # name as a key. We need to get the new files from the files
                # entry to enter into the database.
                # Files lists then get converted to a single string.
                new_files = insertIntoModelFileTable(conn, table_name, 'FILES',
                                                            f[u], f['FILES']) 
                if not new_files == False:
                    log_pages[u][i]['NEW_FILES'] =\
                                        "[" + ", ".join(new_files) + "]"
                
                log_pages[u][i]['FILES'] = "[" + ", ".join(
                                        log_pages[u][i]['FILES']) + "]"
                log_pages[u][i]['ID'] = max_id
                try:
                    DatabaseFunctions.insertValuesIntoTable(conn, u, 
                                                log_pages[u][i])
                except:
                    raise Exception
        
        else:
            # Check if the file already exists in the RUN table or not.
            found_it = False
            try:
                # Get the first entry from tuple which contains a boolean of
                # whether the file exists or not.
                found_it = DatabaseFunctions.findInDatabase('RUN', conn=conn,
                                        col_name=u, db_entry=update_check[u])[0]
            except:
                raise Exception
            
            if not found_it:
                update_check[u] = True
                logger.debug('%s file does not yet exist in database' % (u))
                                            
                # join up the columns and place holders for creating the query.
                log_pages[u]['ID'] = max_id
                try:
                    DatabaseFunctions.insertValuesIntoTable(conn, u, 
                                                    log_pages[u])
                except:
                    raise Exception
            else:
                update_check[u] = False
                logger.debug('%s file already exists in database' % (u))
                
    # Always put an entry in the Run entry table
    max_id = DatabaseFunctions.getMaxIDFromTable(conn, 'RUN') + 1
    log_pages['RUN']['ID'] = max_id
    try:
        DatabaseFunctions.insertValuesIntoTable(conn, 'RUN', 
                                                log_pages['RUN'])
    except:
        raise Exception
    
    return log_pages, update_check


def insertIntoModelFileTable(conn, table_name, col_name, model_file, files_list):
    '''Insert file references into the model file table if they are not
    already there.
    
    @param conn: the current database connection.
    @param table_name: the name of the column to insert the file name into.
    @param file_list: the list of files to check against the database.
    '''
    new_files = []
    for f in files_list:
        
        # Check if we have any matched to the file name.            
        results = DatabaseFunctions.findInDatabase(table_name, conn=conn, 
                    col_name=col_name, db_entry=f, return_rows=True, 
                            only_col_name=False)
        
        # If we didn't find any matches we can put the file into the
        # files database under col_name and add it to the list so that we
        # can put it in the new files col of the main table.
        if results[0] == False:
            row_data = {col_name: model_file, 'FILES': f}
            DatabaseFunctions.insertValuesIntoTable(conn, table_name, row_data)
            new_files.append(f)
    
    if len(new_files) < 1:
        return False
    else:
        return new_files
    
    