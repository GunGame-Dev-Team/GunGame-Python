'''
(c)2008 by the GunGame Coding Team

    Title:      gg_friendlyfire
Version #:      1.15.2008
Description:    Friendlyfire will activate when the last level is reached
'''

import es
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_friendlyfire Addon for GunGame: Python" 
info.version  = "1.15.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_friendlyfire" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"

# Set Level where FF has to be activate
ff = gungame.getTotalLevels() - int(gungame.getGunGameVar("gg_friendlyfire"))

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gg_friendlyfire", "GG FriendlyFire")
    
    # Set mp_friendlyfire to 0
    es.forcevalue("mp_friendlyfire", 0)

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gg_friendlyfire")

def round_start(event_var):
    # Set mp_friendlyfire to 0
    es.forcevalue("mp_friendlyfire", 0)

def gg_levelup(event_var):
    # Delay because gungame core is not fast enough
    gamethread.delayed(0.1, checkff)

def checkff():
    # If the Leader is on the ff level?
    if gungame.getLeaderLevel() == ff:
        # Check whether FF is 0
        if int(es.ServerVar("mp_friendlyfire")) == 0:
            # Set FF to 1; Message and Sound
            es.forcevalue("mp_friendlyfire", 1)
            announce("Friendly fire is now on. Watch your fire.")
            es.cexec_all("play npc/roller/mine/rmine_tossed1.wav")

def announce(message):
    es.msg("#multi", "\4[GG:Friendly Fire]\1 %s" % message)
   
def tell(userid, message):
    es.tell(userid, "#multi", "\4[GG:Friendly Fire]\1 %s" % message)

def echo(message):
    es.dbgmsg(0, "[GG:Friendly Fire] %s" % message)