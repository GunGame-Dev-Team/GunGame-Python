'''
(c)2007 by the GunGame Coding Team

    Title:      gg_error_logging
Version #:      1.0.117
Description:    Logs all errors from gungame and it's addons.
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

gungameErrorLogPath = es.ServerVar('eventscripts_gamedir') + '/addons/eventscripts/gungame/errorlog/errors.log'
dateFormat = '[%A, %B %d, %Y %H:%M:%S]'

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_error_logging Addon for GunGame: Python"
info.version  = "1.0.117"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_error_logging"
info.author   = "GunGame Development Team"

def load():
    # Register addon with gungamelib
    gg_error_logging = gungamelib.registerAddon('gg_error_logging')
    gg_error_logging.setMenuText('GG Error Logging')
    
    sys.excepthook = gungameExceptHook
        
def unload():
    # Unregister addon with gungamelib
    gungamelib.unregisterAddon('gg_error_logging')

def server_cvar(event_var):
    if event_var['cvarname'] == 'gg_error_logging' and event_var['cvarvalue'] == '0':
        es.unload('gg_error_logging')

def gungameExceptHook(type, value, tb):
    gungameError = traceback.format_exception(type, value, tb)
    if 'gungame' in str(gungameError):
        es.dbgmsg(0, 'GunGame Exception Found:')
        if not os.path.isfile(gungameErrorLogPath):
            # Create the Error Log
            gungameErrorLog = open(gungameErrorLogPath, 'w')
            gungameErrorLog.write('GunGame Version: %s\n' %str(es.ServerVar('eventscripts_ggp')))
            gungameErrorLog.write('\n')
        else:
            gungameErrorLog = open(gungameErrorLogPath, 'a')
        gungameErrorLog.write('%s\n' %time.strftime(dateFormat))
        gungameErrorLog.write('-------------------------------------\n')
        for x in gungameError:
            es.dbgmsg(0, x[:-1])
            gungameErrorLog.write('%s\n' %x)
        gungameErrorLog.write('\n')
        gungameErrorLog.close()
    else:
        es.excepter(type, value, tb)