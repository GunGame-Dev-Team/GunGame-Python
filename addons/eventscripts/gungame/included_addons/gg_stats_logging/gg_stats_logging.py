''' (c) 2008 by the GunGame Coding Team

    Title: gg_stats_logging
    Version: 1.0.295
    Description: This addon publishes events for use by third-party stat
                 systems.
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
info.name     = 'gg_stats_logging (for GunGame: Python)'
info.version  = '1.0.295'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_stats_logging'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_stats = gungamelib.registerAddon('gg_stats_logging')
    gg_stats.setDisplayName('GG Stats Logging')

def unload():
    # Unregister
    gungamelib.unregisterAddon('gg_stats_logging')


def gg_levelup(event_var):
    logEvent(event_var['userd'], 'gg_levelup')

def gg_leveldown(event_var):
    logEvent(event_var['userid'], 'gg_leveldown')

def gg_win(event_var):
    logEvent(event_var['userid'], 'gg_win')

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def logEvent(userid, event):
    # Make sure the player exists
    if not es.exists('userid', userid):
        return
    
    # Get player data
    playerName = escape(es.getplayername(userid))
    steamid = escape(es.getplayersteamid(userid))
    teamName = getTeamName(es.getplayerteam(userid))
    
    # Log it
    es.log('%s<%s><%s><%s> triggered %s', playerName, userid, steamid, teamName, event)

def escape(string):
    # Escape string
    string = string.replace(";", "\\;")
    string = string.replace("{", "\\{")
    string = string.replace("}", "\\}")
    string = string.replace("(", "\\(")
    string = string.replace(")", "\\)")
    string = string.replace("'", "\\'")
    string = string.replace(":", "\\:")
    
    # Return
    return string

def getTeamName(team):
    if team == 2:
        return "TERRORIST"
    elif team == 3:
        return "CT"
    else:
        return "UNKNOWN"