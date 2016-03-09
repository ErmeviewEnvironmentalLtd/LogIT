'''
Created on 5 Mar 2016

@author: matthew.shallcross
'''
import os.path
from datetime import datetime as dt
from inspect import stack
from getpass import getuser

# Import logging and get a logger with the name of the module
import logging
logger = logging.getLogger(__name__)

class AppLogger(object):
    '''
    Class for logging APP tool and util usage.
    
    Provides ability to output to the default log path (hardcoded) or a specified path.  
    '''
    def __init__(self, log_path = r"P:\61_R&D\app_logging\app_log.csv"):
        '''
        Constructor
        
        It checks whether the path exists, of it does it warns if the headers are inconsistent,
        if it doesn't it creates the log file with appropriate headers.
        Any read/write error is handled with an exception to prevent interruption to the calling function.
        
        Args:
            log_path (str): path to the log file, Default = r"P:\61_R&D\app_logging\app_log.csv"
            
        Returns:
            None
            
        TODO: Handle incorrect headers by creating new path with incremented verison number (checking
        it doesn't already exist).
            
        '''
        self.log_path = log_path
        self.log_exists = os.path.exists(self.log_path)
        logger.info("I will log to " + self.log_path)
        logger.debug("Does it exist? " + str(self.log_exists))
        #print "I will log to " + self.log_path
        #print "Does it exist? " + str(self.log_exists)
        
        headers = "Timestamp,User,Caller,Message\n"
        
        if not self.log_exists:
            logger.debug("Creating log and headers")
            #print "Creating log and headers"
            
            try:
                with open(self.log_path,'w') as log:            
                    log.write(headers)
            except:
                logger.error("Creating log failed, path: " + self.log_path)
                #print "Creating log failed, path: " + self.log_path
        else:
            logger.debug("Checking headers")
            #print "Checking headers"
            
            try:
                with open(self.log_path,'r') as log:   
                    found_headers = log.readline().strip()         
                    if  found_headers == headers.strip():
                        logger.debug("Headers look good: " + headers.strip())
                        #print "Headers look good: " + headers.strip()
                    else:
                        logger.info("Headers are inconsistant: " + found_headers)
                        #print "Headers are inconsistant: " + found_headers
            except:
                logger.warning("Could not check headers: " + self.log_path)
                #print "Could not check headers: " + self.log_path
        
    def write(self, message = ""):
        '''
        Outputs line to log file.
        
        Log file is currently a basic CSV. If optional message contains commas delimits with double quotes.
        
        Args:
            message (str): Optional log message, Default = ""
            
        Returns:
            None
            
        TODO: Check each string attribute for comma and delimit with double quote if required.
        '''
        # Add double quotes to delimit entries with commas in"
        if ',' in message:
            message = '"' + message + '"'
        
        def build_entry(message):
            '''
                Helper function to build the CSV line
            '''
            try:
                user = getuser()
            except:
                user = "user unknown"                
            try:
                caller = stack()[2][1]
            except:
                caller = "caller unknown"
                
            timestamp = dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S")
            
            return timestamp + ',' + user + ',' + caller + ',' + message + '\n'
        
        try:
            with open(self.log_path,'a') as log:
            
                log.write(build_entry(message))
        except:
            logger.error("Writing to log failed, path: " + self.log_path)
            #print "Writing to log failed, path: " + self.log_path
        
    def getLogPath(self):
        '''
        Args:
            None
            
        Returns:
            self.log_path (str)
        '''
        return self.log_path
    
    def getLogExists(self):
        '''
        Args:
            None
            
        Returns:
            self.log_exists (str)
        '''
        return self.log_exists 