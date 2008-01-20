import sys
import traceback
import es
import os
import time

gungameErrorLogPath = es.ServerVar('eventscripts_gamedir') + '/addons/eventscripts/gungame/errorlog/errors.log'
dateFormat = '[%A, %B %d, %Y %H:%M:%S]'

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_error_logging Addon for GunGame: Python" 
info.version  = "1.19.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_error_logging" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"

def load():
    gungame.registerAddon('gungame/included_addons/gg_error_logging', 'GG Error Logging')
    sys.excepthook = gungameExceptHook
    if not os.path.isfile(gungameErrorLogPath):
        # Create the Error Log
        gungameErrorLog = open(gungameErrorLogPath, 'w')
        gungameErrorLog.close()
        
def unload():
    gungame.unregisterAddon('gungame/included_addons/gg_error_logging')

def gg_variable_changed(event_var):
    if event_var['cvarname'] == 'gg_error_logging' and event_var['newvalue'] == '0':
        es.unload('gungame/included_addons/gg_error_logging')

def gungameExceptHook(type, value, tb):
    gungameError = traceback.format_exception(type, value, tb)
    if 'gungame' in str(gungameError):
        es.dbgmsg(0, 'GunGame Exception Found:')
        if not os.path.isfile(gungameErrorLogPath):
            # Create the Error Log
            gungameErrorLog = open(gungameErrorLogPath, 'w')
        else:
            gungameErrorLog = open(gungameErrorLogPath, 'a')
        gungameErrorLog.write('%s\n' %time.strftime(dateFormat))
        gungameErrorLog.write('-------------------------------------\n')
        for x in gungameError:
            es.dbgmsg(0, x[:-1])
            gungameErrorLog.write('%s\n' %x)
        gungameErrorLog.write('\n')
        gungameErrorLog.close()