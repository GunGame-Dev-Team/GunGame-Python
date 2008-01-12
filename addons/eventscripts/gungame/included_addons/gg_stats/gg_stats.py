'''
(c)2008 by the GunGame Coding Team

    Title:      gg_stats
Version #:      1.7.2008
Description:    This is an addon only for HLStatsX Users. This addon allows HLStatsX to read out the stats!
'''

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_stats Addon for GunGame: Python" 
info.version  = "1.7.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_stats" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gungame/included_addons/gg_stats", "GG Stats")

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gungame/included_addons/gg_stats")

def escs(string):
    # Escape string
    string = string.replace(";", "\;")
    string = string.replace("{", "\{")
    string = string.replace("}", "\}")
    string = string.replace("(", "\(")
    string = string.replace(")", "\)")
    string = string.replace("'", "\'")
    string = string.replace(":", "\:")
    
    # Return
    return string

def gg_levelup(event_var):
    # Set team to None
    team = None
    
    # Get team
    if event_var["team"] == 2:
        team = "CT"
    else:
        team = "TERRORIST"
    
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\levelup" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), team))

def gg_leveldown(event_var):
    # Set team to None
    team = None
    
    # Get team
    if event_var["team"] == 2:
        team = "CT"
    else:
        team = "TERRORIST"
    
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\leveldown" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), team))

def gg_win(event_var):
    # Set team to None
    team = None
    
    # Get team
    if event_var["team"] == 2:
        team = "CT"
    else:
        team = "TERRORIST"
    
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\win" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), team))