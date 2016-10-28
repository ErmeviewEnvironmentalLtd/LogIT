"""
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


 Module:  Exporters.py
 Date:    16/11/2014
 Author:  Duncan Runnacles. This is taken, almost completely from someone's
          blog and I can't remember or find out who it was. If you wrote this
          please contact me and I will provide credit.
 Version:  0.1
 
 Summary:
    Contains all the functions required to export data from the database to
    other formats. Currently the only export available is to Excel.

 UPDATES:
    DR - 19/11/2014
        Changed the way that column data is written to worksheets. Now uses
        DatabaseFunctions.cur_tables order rather than database order.
    DR - 08/09/2016:
       Complete re-write and simplification to use the new style outputs from
       the new peewee database backend.
       No longer writes the sqlite tables directly to worksheets. Now takes 
       formatted dicts and list for the required tables and writes them
       instead.

 TODO:

###############################################################################
"""

# Import python standard modules
import sqlite3 as sqlite
import os
import logging
logger = logging.getLogger(__name__)

# Import Excel writer
try:
    import xlwt
except:
    logger.error('Cannot import xlwt (is it installed?):\n'+
                  'Cannot export database to Excel')  


def newExportToExcel(run, runh, dat, dath, model, ied, iedh, xlspath):
    """Export database data to Excel .xls format.
    
    Args:
        run(dict): containing lists with output variables for each run id.
        runh(list): column headers for run data.
        dat(dict): containing lists with output variables for each dat id.
        dath(list): column headers for dat data.
        model(dict): containing sub-dicts for each model_type (TGC, etc) which
            in turn contain sub-dicts for ModelFile columns.
        ied(dict): containing lists with output variables for each ied id.
        iedh(list): column headers for ied data.
        xlspath(str): path to write the workbook to.
    """
    # Create a workbook and add the Run worksheet
    w = xlwt.Workbook()
    ws = w.add_sheet('RUN')  
    
    # Write the run headers
    logger.info('create Worksheet: RUN')
    for i, h in enumerate(runh): 
        ws.write(0, i, h)
    
    # Write the run data for each entry in the dict
    count = 1
    for k, v in run.items():
        max = len(v) - 1
        for j, r in enumerate(v):
            if j == max:
                ws.write(count, j, ', '.join(r))
            else:
                ws.write(count, j, r)
        count += 1
    
    # Write the Dat headers
    logger.info('create Worksheet: DAT')
    ws = w.add_sheet('DAT')
    for i, h in enumerate(dath, 0): 
        ws.write(0, i, h)
    
    # Write the dat data for each entry in the dict
    count = 1
#     for k, v in dat.items():
    for v in dat:
        for j, d in enumerate(v, 0):
            ws.write(count, j, d)
        count += 1
    
    # Write the Ied headers
    logger.info('Create Worksheet: IED')
    ws = w.add_sheet('IED')
    for i, h in enumerate(iedh, 0):
        ws.write(0, i, h)
    
    # Write the ied data for each entry
    count = 1
    for v in ied:
        for j, i in enumerate(v, 0):
            ws.write(count, j, i)
        count += 1
    
    # Create a different worksheet for each model_type (TGC, TBC, etc)
    headers = ['Name', 'Date', 'Comments', 'Files', 'New Files']
    for mtype, models in model.items():
        ws = w.add_sheet(mtype)
        
        # Write the ModelFile headers
        logger.info('create Worksheet: ' + str(mtype))
        for i, h in enumerate(headers, 0):
            ws.write(0, i, h)
        
        # Write the row data for each entry in this model_type
        count = 1
        for m in models:
            ws.write(count, 0, m['name'])
            ws.write(count, 1, m['date'])
            ws.write(count, 2, m['comments'])
            ws.write(count, 3, ', '.join(m['files']))
            ws.write(count, 4, ', '.join(m['new_files']))
            count += 1
        
    w.save(xlspath) 
    
    
