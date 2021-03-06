''' (c) 2008 by the GunGame Coding Team

    Title: gg_unl_grenade
    Version: 5.0.558
    Description: When a player reaches grenade level, they are given another 
                 grenade when their  thrown grenade detonates.  This will
                 automatically disable the gg_earn_nade addon.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_unl_grenade (for GunGame5)'
info.version  = '5.0.558'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_unl_grenade'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_unl_grenade = gungamelib.registerAddon('gg_unl_grenade')
    gg_unl_grenade.setDisplayName('GG Unlimited Grenade')
    gg_unl_grenade.addDependency('gg_earn_nade', 0)
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_unl_grenade')
    
def hegrenade_detonate(event_var):
    userid = event_var['userid']
    gungamePlayer = gungamelib.getPlayer(userid)
    playerlibPlayer = playerlib.getPlayer(userid)
    
    if event_var['es_userteam'] > 1 and gungamePlayer.getWeapon() == 'hegrenade' and not int(playerlibPlayer.get('isdead')):
        es.server.queuecmd('es_xgive %s weapon_hegrenade' % userid)