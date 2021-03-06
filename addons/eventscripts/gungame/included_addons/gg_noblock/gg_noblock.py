''' (c) 2008 by the GunGame Coding Team

    Title: gg_noblock
    Version: 5.0.402
    Description: No-block addon for GunGame:Python.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Eventscripts imports
import es

# Gungame import
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_noblock (for GunGame5)'
info.version  = '5.0.402'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_noblock'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_noblock = gungamelib.registerAddon('gg_noblock')
    gg_noblock.setDisplayName('GG Noblock')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_noblock')


def player_spawn(event_var):
    userid = int(event_var['userid'])
    
    # Make non-solid
    es.setplayerprop(userid, 'CBaseEntity.m_CollisionGroup', 2)