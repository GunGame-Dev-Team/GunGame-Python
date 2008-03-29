''' (c) 2008 by the GunGame Coding Team

    Title: gg_friendlyfire
    Version: 1.0.212
    Description: Friendly fire will activate when a certain level is reached.
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
info.name     = 'gg_friendlyfire (for GunGame: Python)'
info.version  = '1.0.210'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_friendlyfire'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
levelVariable = gungamelib.getVariable('gg_friendlyfire')
int_ffBackup = 0

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_friendlyfire = gungamelib.registerAddon('gg_friendlyfire')
    gg_friendlyfire.setMenuText('GG FriendlyFire')
    
    # Get backup of mp_friendlyfire
    int_ffBackup = int(es.ServerVar('mp_friendlyfire'))
    
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_friendlyfire')
    
    # Return 'mp_friendlyfire' to what it was originally
    es.server.cmd('mp_friendlyfire %d' % int_ffBackup)

def es_map_start(event_var):
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)
    
def gg_start(event_var):
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)

def gg_levelup(event_var):
    # Get activation level
    activateLevel = gungamelib.getTotalLevels() - int(levelVariable)
    
    # If the Leader is on the friendlyfire level?
    if gungamelib.getLeaderLevel() >= activateLevel:
        # Check whether friendlyfire is enabled
        if int(es.ServerVar('mp_friendlyfire')) == 0:
            # Set friendlyfire to 1
            es.forcevalue('mp_friendlyfire', 1)
            
            # Show message and sound
            gungamelib.msg('gg_friendlyfire', '#all', 'WatchYourFire')
            es.cexec_all('play npc/roller/mine/rmine_tossed1.wav')