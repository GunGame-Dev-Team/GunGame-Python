''' (c) 2008 by the GunGame Coding Team

    Title: gg_error_logging
    Version: 1.0.285
    Description: Logs all errors raised by GunGame and its addons.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import sys
import os
import time
import traceback

# EventScripts imports
import es
import popuplib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_error_logging Addon for GunGame: Python'
info.version  = '1.0.285'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_error_logging'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
dict_errorTracking = {}
dateFormat = '%d/%m/%Y @ [%H:%M:%S]'
errorFile = None

# ==============================================================================
#  ERROR TRACKING CLASS
# ==============================================================================
class ErrorTracking:
    '''Tracks the count and line number of the errors that are logged.'''
    errorIndex = None
    errorCount = 1

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global errorFile
    
    # Register addon with gungamelib
    gg_error_logging = gungamelib.registerAddon('gg_error_logging')
    gg_error_logging.setDisplayName('GG Error Logging')
    
    # Clear existing logs
    clearExistingLogs()
    
    # Set error hook
    sys.excepthook = exceptHook
    
    logPath = gungamelib.getGameDir('addons/eventscripts/gungame/logs/errorlog %s.txt' % es.ServerVar('eventscripts_ggp'))
    
    # Don't print header if the file already exists
    if os.path.isfile(logPath):
        return
    
    # Print opening header
    openFile('w')
    errorFile.write('\n')
    errorFile.write('%s\n' % ('*' * 50))
    errorFile.write('  GunGame Errorlog\n')
    errorFile.write('  Opened: %s\n' % time.strftime(dateFormat))
    errorFile.write('\n')
    errorFile.write('  Version Information:\n')
    
    # Print version information
    errorFile.write('    * EventScripts: %s\n' % es.ServerVar('eventscripts_ver'))
    
    # Only print EST information if its installed
    if gungamelib.hasEST():
        errorFile.write('    * ES_Tools: %s\n' % es.ServerVar('est_version'))
    else:
        errorFile.write('    * ES_Tools: (Not Installed)\n')
    
    errorFile.write('    * GunGame: %s\n' % es.ServerVar('eventscripts_ggp'))
    errorFile.write('    * Popup: %s\n' % popuplib.info.version)
    
    # Finish
    errorFile.write('%s\n' % ('*' * 50))
    errorFile.write('\n')
    errorFile.close()

def unload():
    # Unregister addon with gungamelib
    gungamelib.unregisterAddon('gg_error_logging')

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def clearExistingLogs():
    # Get base directory
    baseDir = gungamelib.getGameDir('addons/eventscripts/gungame/logs/')
    
    # Loop through the files
    for f in os.listdir(baseDir):
        # Get name and extension
        name, ext = os.path.splitext(f)
        
        # Is an old log file?
        if ext == '.log':
            os.remove(baseDir + f)
            continue
        
        # Isn't a text file?
        if ext != '.txt':
            continue
        
        # Name doesn't start with errorlog?
        if not name.startswith('errorlog '):
            continue
        
        # Remove the file
        if name != str(es.ServerVar('eventscripts_ggp')):
            os.remove(baseDir + f)

def openFile(type):
    global errorFile
    
    # Get path
    logPath = gungamelib.getGameDir('addons/eventscripts/gungame/logs/errorlog %s.txt' % es.ServerVar('eventscripts_ggp'))

    # Open the file
    errorFile = open(logPath, type)

def exceptHook(type, value, tb):
    global errorFile
    
    # Format exception
    gungameError = traceback.format_exception(type, value, tb)
    
    # If not a gungame error, send to ES and return
    if 'gungame' not in str(gungameError):
        es.excepter(type, value, tb)
        return
    
    # Print header
    es.dbgmsg(0, '\n%s' % ('*' * 79))
    es.dbgmsg(0, '  GunGame exception caught!')
    es.dbgmsg(0, '%s\n' % ('*' * 79))
    
    # Check for previous occurences of the same bug
    gungameErrorCheck = gungameError[:]
    gungameErrorCheck.pop()
    gungameErrorCheck = str(gungameErrorCheck)
    
    # Does the error already exist?
    if dict_errorTracking.has_key(gungameErrorCheck):
        # Increment the error count
        dict_errorTracking[gungameErrorCheck].errorCount += 1
        
        # Format the new line's text
        newText = '  Exception caught: %s [Occurences: %s]\n' % (time.strftime(dateFormat), dict_errorTracking[gungameErrorCheck].errorCount)
        
        # Execute the change of the new line so it will write to the error log
        replaceErrorLine(dict_errorTracking[gungameErrorCheck].errorIndex, newText)
        
        # Echo the error to the console
        for x in gungameError:
            es.dbgmsg(0, x[:-1])
    else:
        # Add the new error to the dict_errorTracking
        dict_errorTracking[gungameErrorCheck] = ErrorTracking()
        dict_errorTracking[gungameErrorCheck].errorIndex = getErrorLine()
        
        # Open the file for writing
        openFile('a')
        
        # Write header to file
        errorFile.write('\n')
        errorFile.write('%s\n' % ('-=' * 33))
        errorFile.write('  Exception caught: %s [Occurences: %s]\n' % (time.strftime(dateFormat), dict_errorTracking[gungameErrorCheck].errorCount))
        errorFile.write('%s\n' % ('-=' * 33))
        errorFile.write('\n')
        
        # Write the error
        for x in gungameError:
            es.dbgmsg(0, x[:-1])
            errorFile.write('%s\n' % x)
        
        # Flush the changes, and close
        errorFile.write('\n')
        errorFile.flush()
        errorFile.close()
    
    # Print finishing
    es.dbgmsg(0, '\n%s' % ('*' * 79))
    es.dbgmsg(0, '  Please open "addons/eventscripts/gungame/logs/errorlog %s.txt" and' % es.ServerVar('eventscripts_ggp'))
    es.dbgmsg(0, '  report the bug in the "Bug Reports" topic.')
    es.dbgmsg(0, '%s\n' % ('*' * 79))
    
def getErrorLine():
    global errorFile
    
    # Open the file for reading
    openFile('r')
    
    # Check the total lines in the errorlog
    lineCount = len(errorFile.readlines()) + 2
    
    # Close the file
    errorFile.close()
    
    return lineCount
    
def replaceErrorLine(lineIndex, text):
    global errorFile
    
    # Open the file for reading
    openFile('r')
    
    # Create a list for modification of the line containing the error count and update the list
    list_errorLogLines = errorFile.readlines()
    list_errorLogLines.pop(lineIndex)
    list_errorLogLines.insert(lineIndex, text)
    
    # Close the file
    errorFile.close()
    
    # Open the file for writing
    openFile('w')
    
    # Re-write the errors to the file with the modified information
    for line in list_errorLogLines:
        errorFile.write(line)
    
    # Flush the changes, and close
    errorFile.flush()
    errorFile.close()