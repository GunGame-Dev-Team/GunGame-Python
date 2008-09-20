''' (c) 2008 by the GunGame Coding Team

    Title: gg_stats_logging
    Version: 1.0.472
    Description: This addon publishes events for use by third-party statistic
                 applications.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_stats_logging (for GunGame: Python)'
info.version  = '1.0.472'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_stats_logging'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
events = []

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global events
    
    this = __import__(__name__)
    
    # Register
    gg_stats = gungamelib.registerAddon('gg_stats_logging')
    gg_stats.setDisplayName('GG Stats Logging')
    
    # Get file
    for line in gungamelib.getFileLines('cfg/gungame/stats_logging.txt'):
        es.addons.registerForEvent(this, line, logEvent)
        events.append(line)

def unload():
    global events
    
    this = __import__(__name__)
    
    # Unregister
    gungamelib.unregisterAddon('gg_stats_logging')
    
    # Unregister events
    for event in events:
        es.addons.unregisterForEvent(this, event)

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def logEvent(event_var):
    # Get event info
    event = event_var['es_event']
    userid = event_var['userid']
    
    if event in ('gg_levelup', 'gg_knife_steal', 'gg_win'):
        userid = event_var['attacker']
    
    # Make sure the player exists
    if not gungamelib.clientInServer(userid):
        return
    
    # Get player data
    playerName = es.getplayername(userid)
    steamid = es.getplayersteamid(userid)
    teamName = getTeamName(es.getplayerteam(userid))
    
    # Log it
    es.server.queuecmd('es_xlogq "%s<%s><%s><%s>" triggered "%s"' % (playerName, userid, steamid, teamName, event))

def getTeamName(team):
    if team == 2:
        return 'TERRORIST'
    elif team == 3:
        return 'CT'
    else:
        return 'UNKNOWN'