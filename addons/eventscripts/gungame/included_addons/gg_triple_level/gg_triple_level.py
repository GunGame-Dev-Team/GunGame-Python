'''
(c)2008 by the GunGame Coding Team

    Title:      gg_triple_level
Version #:      1.12.2008
Description:    When a player makes 3 levels in one round he get faster and have an effect for 10 secs
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_triple_level Addon for GunGame: Python" 
info.version  = "1.5.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_triple_level" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"

# Dic for Triple Level

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gungame/included_addons/gg_triple_level", "GG Triple Level")

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gungame/included_addons/gg_triple_level")

def gg_levelup(event_var):
    # If is it a Triple Level
    tripler = gungame.getPlayer(event_var["userid"])
    
    if tripler.get("triple") == 3:
        # Sound and Messages
        es.emitsound("player", event_var["userid"], gungame.getGunGameVar("gg_sound_triple"), 1.0, 1.0)
        es.msg("#multi", "#green%s#lightgreen triple levelled!!!" % event_var["name"])
        es.centermsg("%s triple levelled!!!" % event_var["name"])
        
        # Effect to player
        es.give(event_var["userid"], "env_spark")
        es.fire(event_var["userid"], "env_spark", "setparent", "!activator")
        es.fire(event_var["userid"], "env_spark", "addoutput", "spawnflags 896")
        es.fire(event_var["userid"], "env_spark", "addoutput", "angles -90 0 0")
        es.fire(event_var["userid"], "env_spark", "addoutput", "magnitude 8")
        es.fire(event_var["userid"], "env_spark", "addoutput", "traillength 3")
        es.fire(event_var["userid"], "env_spark", "startspark")
        
        # Speed
        player = playerlib.getPlayer(event_var["userid"])
        player.set("speed", 1.5)
        
        # Gravity
	  # THIS IS ONLY A TEST TO MAKE IT WITHOUT EST!
        es.give(event_var["userid"], "trigger_gravity")
        es.fire(event_var["userid"], "trigger_gravity", "setparent", "!activator")
        es.fire(event_var["userid"], "trigger_gravity", "addoutput", "gravity 0.55")
        es.fire(event_var["userid"], "trigger_gravity", "enable")
	  # THIS IS ONLY A TEST TO MAKE IT WITHOUT EST!
        
        # Stop Triple Level Bonus after 10 secs
        gamethread.delayed(10, removetriple, event_var["userid"])

def removetriple(userid):
    # Check if UserID exists
    # In the 10 secs the user maybe left
    if es.exists("userid", userid):
        # Stop Effect
        es.fire(userid, "env_spark", "stopspark")
        
        # Stop Speed
        player = playerlib.getPlayer(userid)
        player.set("speed", 1)
        
        # Stop Gravity
	  # THIS IS ONLY A TEST TO MAKE IT WITHOUT EST!
        es.fire(userid, "trigger_gravity", "disable")
	  # THIS IS ONLY A TEST TO MAKE IT WITHOUT EST!
    else:
        # Echo debug message, the user left
        es.dbgmsg(1, "GunGame: Python Triple Level Addon: Can't remove triple bonus, user left")