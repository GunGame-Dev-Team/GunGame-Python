''' (c) 2008 by the GunGame Coding Team

    Title: gg_stats
    Version: 1.0.223
    Description: This is an addon only for HLStatsX Users.
                 It allows HLStatsX to read out the stats.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_stats (for GunGame: Python)'
info.version  = '1.0.223'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_stats'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_stats = gungamelib.registerAddon('gg_stats')
    gg_stats.setDisplayName('GG Stats')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_stats')


def gg_levelup(event_var):
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_levelup" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))

def gg_leveldown(event_var):
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_\eveldown" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))

def gg_win(event_var):
    # Publish to server
    es.server.cmd("es_logq %s<%i><%s><%s> triggered gg_win" % (escs(event_var["name"]), event_var["userid"], escs(event_var["steamid"]), cteam(event_var["team"])))

def cteam(team):
    if team == 2:
        return "TERRORIST"
    
    return "CT"

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
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