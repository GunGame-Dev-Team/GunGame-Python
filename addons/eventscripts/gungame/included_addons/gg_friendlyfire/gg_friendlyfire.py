''' (c) 2008 by the GunGame Coding Team

    Title: gg_friendlyfire
    Version: 5.0.558
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
info.name     = 'gg_friendlyfire (for GunGame5)'
info.version  = '5.0.558'
info.url      = 'http://gungame5.com/'
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
    gg_friendlyfire.setDisplayName('GG FriendlyFire')
    gg_friendlyfire.loadTranslationFile()
    
    # Get backup of mp_friendlyfire
    int_ffBackup = int(es.ServerVar('mp_friendlyfire'))
    
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_friendlyfire')
    
    # Return 'mp_friendlyfire' to what it was originally
    es.server.queuecmd('mp_friendlyfire %d' % int_ffBackup)

def es_map_start(event_var):
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)
    
def gg_start(event_var):
    # Set mp_friendlyfire to 0
    es.forcevalue('mp_friendlyfire', 0)

def gg_levelup(event_var):
    # Get activation level
    activateLevel = gungamelib.getTotalLevels()+1 - int(levelVariable)
    
    # If the Leader is on the friendlyfire level?
    if gungamelib.leaders.getLeaderLevel() >= activateLevel:
        # Check whether friendlyfire is enabled
        if int(es.ServerVar('mp_friendlyfire')) == 0:
            # Set friendlyfire to 1
            es.forcevalue('mp_friendlyfire', 1)
            
            # Show message and sound
            gungamelib.msg('gg_friendlyfire', '#all', 'WatchYourFire')
            gungamelib.playSound('#all', 'friendlyfire')