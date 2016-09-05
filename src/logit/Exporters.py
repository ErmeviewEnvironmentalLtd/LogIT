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

 TODO:

###############################################################################
"""

# Import python standard modules
import sqlite3 as sqlite
import os
import logging
import DatabaseFunctions
logger = logging.getLogger(__name__)

# Import Excel writer
try:
    import xlwt
except:
    logger.error('Cannot import xlwt (is it installed?):\n'+
                  'Cannot export database to Excel')  

def sqlite_get_col_names(cur, table):
    """Get the names of the columns in the given table.
    
    :param cur: the cursor to the currently connected database.
    :param table: the table to be queried.
    :return: the column names.
    """
    query = 'select * from  %s' % table
    cur.execute(query)
    return [tuple[0] for tuple in cur.description]  
  
def sqlite_query(cur,  table, col = '*', where = ''):  
    """Run an sql query with the given parameters.
    
    :param cur: the cursor to the currently connected database.
    :param table: the table to be queried.
    :param col: the column(s) to return.
    :param where: the WHERE criteria for the sql connection.
    """
    if where != '':  
        query = 'select %s from %s where %s' % (col, table, where)  
    else:  
        query = 'select %s from %s ' % (col, table)  
    cur.execute(query)  
    return cur.fetchall()  
  

def sqlite_to_workbook(cur, table, workbook, keep_tables):  
    """convert Sqlite3 data base to an excel workbook.
    Converts the sqlite3 table at the given database cursor to an Excel (.xls)
    Worksheet. This Worksheet will then be added to the given Workbook object.
    
    :param cur: the cursor to the currently connected database.
    :param table: the table to convert to a worksheet.
    :param workbook: the workbook to which the worksheet will be added.
    """
    if table in keep_tables:
        ws = workbook.add_sheet(table)  
        logger.info('create Worksheet %s.'  % table)
    
        for colx, heading in enumerate(sqlite_get_col_names(cur, table)):  
                ws.write(0,colx, heading)  
        for rowy,row in enumerate(sqlite_query(cur, table)):  
            for colx, text in enumerate(row):  
                ws.write(rowy+ 1, colx, text)
#         for colx, heading in enumerate(DatabaseFunctions.cur_tables[table]):
#                 ws.write(0,colx, heading)
#         for rowy,row in enumerate(sqlite_query(cur, table)):  
#             for colx, text in enumerate(row):  
#                 ws.write(rowy+ 1, colx, text)  
  

def exportToExcel(dbpath, keep_tables, excel_path=None):  
    """Convert the database at the given path to an Excel (.xls) Workbook where
    each table in the database if a different Worksheet.
    The newly created Excel Workbook will be saved in the same location as the
    database.
    
    :param dbpath: the path to the sqlite3 database to be converted to Excel.
    """
    if excel_path == None:
        dir_path, fname = os.path.split(dbpath)
        fname = os.path.splitext(fname)[0]
        xlspath = os.path.join(dir_path, fname + '.xls')
    else:
        xlspath = excel_path
        
    logger.info("Converting <%s> --> <%s>"% (dbpath, xlspath))
  
    db = sqlite.connect(dbpath)  
    cur = db.cursor()  
    w = xlwt.Workbook()  
    for tbl_name in [row[0] for row in sqlite_query(cur, 'sqlite_master', 'tbl_name', 'type = \'table\'')]:  
        sqlite_to_workbook(cur,tbl_name, w, keep_tables)
          
    cur.close()  
    db.close()  
    if tbl_name !=[]: w.save(xlspath)  
    

def newExportToExcel(run, runh, dat, dath, model, xlspath):
    
    w = xlwt.Workbook()
    ws = w.add_sheet('Run')  
    logger.info('create Worksheet: Run')
    for i, h in enumerate(runh): 
        ws.write(0, i, h)
    
    count = 1
    for k, v in run.items():
        max = len(v) - 1
        for j, r in enumerate(v):
            if j == max:
                ws.write(count, j, ', '.join(r))
            else:
                ws.write(count, j, r)
        count += 1
    
    ws = w.add_sheet('Dat')
    for i, h in enumerate(dath, 0): 
        ws.write(0, i, h)
    
    count = 1
    for k, v in dat.items():
        for j, d in enumerate(v, 0):
            ws.write(count, j, d)
        count += 1
    
    headers = ['Name', 'Date', 'Comments', 'Files', 'New Files']
    for mtype, models in model.items():
        ws = w.add_sheet(mtype)
        
        for i, h in enumerate(headers, 0):
            ws.write(0, i, h)
        
        count = 1
        for k, m in models.items():
            ws.write(count, 0, k)
            ws.write(count, 1, models[k]['date'])
            ws.write(count, 2, models[k]['comments'])
            ws.write(count, 3, ', '.join(models[k]['files']))
            ws.write(count, 4, ', '.join(models[k]['new_files']))
            count += 1
        
    w.save(xlspath) 
    
    
