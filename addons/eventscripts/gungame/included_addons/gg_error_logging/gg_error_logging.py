''' (c) 2008 by the GunGame Coding Team

    Title: gg_error_logging
    Version: 1.0.209
    Description: Logs all errors raised by GunGame and its addons.
'''

# Python imports
import sys
import traceback
import os
import time

# EventScripts imports
import es

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_error_logging Addon for GunGame: Python"
info.version  = "1.0.209"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_error_logging"
info.author   = "GunGame Development Team"

# Globals
dateFormat = '%d/%m/%Y @ [%H:%M:%S]'
errorFile = None

def load():
    global errorFile
    
    # Register addon with gungamelib
    gg_error_logging = gungamelib.registerAddon('gg_error_logging')
    gg_error_logging.setMenuText('GG Error Logging')
    
    # Clear existing logs
    clearExistingLogs()
    
    # Print opening header
    openFile()
    errorFile.write('\n')
    errorFile.write('%s\n' % ('*' * 50))
    errorFile.write('\tGunGame Errorlog\n')
    errorFile.write('\tOpened: %s\n' % time.strftime(dateFormat))
    errorFile.write('%s\n' % ('*' * 50))
    errorFile.write('\n')
    errorFile.close()
    
    # Set error hook
    sys.excepthook = exceptHook

def unload():
    # Unregister addon with gungamelib
    gungamelib.unregisterAddon('gg_error_logging')

def server_cvar(event_var):
    if event_var['cvarname'] == 'gg_error_logging' and event_var['cvarvalue'] == '0':
        es.unload('gg_error_logging')

def clearExistingLogs():
    # Get base directory
    baseDir = gungamelib.getGameDir('addons/eventscripts/gungame/errorlog/')
    
    # Loop through the files
    for f in os.listdir(baseDir):
        name, ext = os.path.splitext(f)
        
        # Is an old log file?
        if ext == '.log':
            os.remove(baseDir + f)
            continue
        
        # Isn't a text file?
        if ext != '.txt':
            continue
        
        # Remove the file
        if name != str(es.ServerVar('eventscripts_ggp')):
            os.remove(baseDir + f)

def openFile():
    global errorFile
    
    # Get path
    logPath = gungamelib.getGameDir('addons/eventscripts/gungame/errorlog/%s.txt' % str(es.ServerVar('eventscripts_ggp')))

    # Open the file
    errorFile = open(logPath, 'a')

def exceptHook(type, value, tb):
    global errorFile
    
    # Format exception
    gungameError = traceback.format_exception(type, value, tb)
    
    # If not a gungame error, send to ES
    if 'gungame' not in str(gungameError):
        es.excepter(type, value, tb)
    
    # Print header
    es.dbgmsg(0, '\n%s' % ('*' * 79))
    es.dbgmsg(0, 'GunGame exception caught!')
    es.dbgmsg(0, '%s\n' % ('*' * 79))
    
    # Open the file for writing
    openFile()
    
    # Write header to file
    errorFile.write('\n')
    errorFile.write('%s\n' % ('-=' * 25))
    errorFile.write('\tException caught: %s\n' % time.strftime(dateFormat))
    errorFile.write('%s\n' % ('-=' * 25))
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
    es.dbgmsg(0, 'Please open "addons/eventscripts/gungame/errorlog/%s.txt" and report the' % str(es.ServerVar('eventscripts_ggp')))
    es.dbgmsg(0, 'error in the GunGame "Bug Reports" topic.')
    es.dbgmsg(0, '%s\n' % ('*' * 79))