'''
(c)2008 by the GunGame Coding Team

    Title:      gg_stats
Version #:      1.0.158
Description:    This is an addon only for HLStatsX Users. This addon allows HLStatsX to read out the stats!
'''

# EventScripts imports
import es

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_stats Addon for GunGame: Python"
info.version  = "1.0.158"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_stats"
info.author   = "GunGame Development Team"

def load():
    # Register addon with gungamelib
    gg_stats = gungamelib.registerAddon('gg_stats')
    gg_stats.setMenuText('GG Stats')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_stats')

def cteam(team):
    if team == 2:
        return "TERRORIST"
    
    return "CT"

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
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\levelup" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))

def gg_leveldown(event_var):
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\leveldown" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))

def gg_win(event_var):
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\win" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))