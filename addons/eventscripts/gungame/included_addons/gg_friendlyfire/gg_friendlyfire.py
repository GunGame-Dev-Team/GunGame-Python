'''
(c)2008 by the GunGame Coding Team

    Title:      gg_friendlyfire
Version #:      1.0.86
Description:    Friendlyfire will activate when the last level is reached
'''

import es
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_friendlyfire Addon for GunGame: Python" 
info.version  = "1.0.86"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_friendlyfire" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"

# Set Level where gg_friendlyfire has to be activate
friendlyFireLevel = gungame.getTotalLevels() - int(gungame.getGunGameVar("gg_friendlyfire"))
friendlyFireEnabled = 0
mp_friendlyfireBackUp = 0

def load():
    global mp_friendlyfireBackUp
    
    # Register this addon with GunGame
    gungame.registerAddon("gg_friendlyfire", "GG FriendlyFire")
    
    # Get backup of mp_friendlyfire
    mp_friendlyfireBackUp = int(es.ServerVar('mp_friendlyfire'))
    # Set mp_friendlyfire to 0
    es.forcevalue("mp_friendlyfire", 0)

def unload():
    global mp_friendlyfireBackUp
    
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gg_friendlyfire")
    
    # Return "mp_friendlyfire" to what it was originally
    es.server.cmd('mp_friendlyfire %d' %mp_friendlyfireBackUp)
    
def gg_variable_changed(event_var):
    global friendlyFireLevel
    # Watch for change in friendlyfire level
    if event_var['cvarname'] == 'gg_friendlyfire':
        friendlyFireLevel = gungame.getTotalLevels() - int(event_var['newvalue'])

def es_map_start(event_var):
    global friendlyFireEnabled
    
    friendlyFireEnabled = 0
    # Set mp_friendlyfire to 0
    es.forcevalue("mp_friendlyfire", 0)
    
def gg_start():
    global friendlyFireEnabled
    global friendlyFireLevel
    
    friendlyFireEnabled = 0
    # Set mp_friendlyfire to 0
    es.forcevalue("mp_friendlyfire", 0)
    
    # Get friendlyfireLevel again just incase the Total Levels have changed
    friendlyFireLevel = gungame.getTotalLevels() - int(gungame.getGunGameVar("gg_friendlyfire"))
    

def gg_levelup(event_var):
    global friendlyFireEnabled
    global friendlyFireLevel
    
    # If the Leader is on the friendlyfire level?
    if gungame.getLeaderLevel() >= friendlyFireLevel:
        # Check whether friendlyfire is enabled
        if not friendlyFireEnabled:
            # Set friendlyfire to 1; Message and Sound
            es.forcevalue("mp_friendlyfire", 1)
            announce("Friendly fire is now on. Watch your fire.")
            es.cexec_all("play npc/roller/mine/rmine_tossed1.wav")
            friendlyFireEnabled = 1

def announce(message):
    es.msg("#multi", "\4[GG:Friendly Fire]\1 %s" % message)
   
def tell(userid, message):
    es.tell(userid, "#multi", "\4[GG:Friendly Fire]\1 %s" % message)

def echo(message):
    es.dbgmsg(0, "[GG:Friendly Fire] %s" % message)