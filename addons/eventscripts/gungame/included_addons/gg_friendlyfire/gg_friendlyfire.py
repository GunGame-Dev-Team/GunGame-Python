'''
(c)2008 by the GunGame Coding Team

    Title:      gg_friendlyfire
Version #:      1.0.144
Description:    Friendly fire will activate when the last level is reached
'''

# EventScripts imports
import es
import gamethread

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_friendlyfire Addon for GunGame: Python"
info.version  = "1.0.144"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_friendlyfire"
info.author   = "GunGame Development Team"

# Set Level where gg_friendlyfire has to be activate
friendlyFireLevel = gungamelib.getTotalLevels() - gungamelib.getVariableValue('gg_friendlyfire')
friendlyFireEnabled = 0
mp_friendlyfireBackUp = 0

def load():
    # Register addon with gungamelib
    gg_friendlyfire = gungamelib.registerAddon('gg_friendlyfire')
    gg_friendlyfire.setMenuText('GG FriendlyFire')
    
    # Get backup of mp_friendlyfire
    mp_friendlyfireBackUp = int(es.ServerVar('mp_friendlyfire'))
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_friendlyfire')
    
    # Return 'mp_friendlyfire' to what it was originally
    es.server.cmd('mp_friendlyfire %d' %mp_friendlyfireBackUp)
    
def server_cvar(event_var):
    # Watch for change in friendlyfire level
    if event_var['cvarname'] == 'gg_friendlyfire':
        friendlyFireLevel = gungamelib.getTotalLevels() - int(event_var['cvarvalue'])

def es_map_start(event_var):
    friendlyFireEnabled = 0
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)
    
def gg_start():
    friendlyFireEnabled = 0
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)
    
    # Get friendlyfireLevel again just incase the Total Levels have changed
    friendlyFireLevel = gungamelib.getTotalLevels() - gungamelib.getVariableValue('gg_friendlyfire')
    

def gg_levelup(event_var):
    # If the Leader is on the friendlyfire level?
    if gungamelib.getLeaderLevel() >= friendlyFireLevel:
        # Check whether friendlyfire is enabled
        if not friendlyFireEnabled:
            # Set friendlyfire to 1; Message and Sound
            es.forcevalue('mp_friendlyfire', 1)
            gungamelib.msg('gg_friendlyfire', '#all', 'WatchYourFire')
            es.cexec_all('play npc/roller/mine/rmine_tossed1.wav')
            friendlyFireEnabled = 1