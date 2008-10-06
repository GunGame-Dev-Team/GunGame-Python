''' (c) 2008 by the GunGame Coding Team

    Title: gg_nade_bonus
    Version: 1.0.476
    Description: When players are on grenade level, by default, they are just given
                 an hegrenade. This addon will give them an additional weapon of the
                 admin's choice.
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
info.name     = 'gg_nade_bonus (for GunGame: Python)'
info.version  = '1.0.476'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_nade_bonus'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_nade_bonus = gungamelib.registerAddon('gg_nade_bonus')
    gg_nade_bonus.setDisplayName('GG Nade Bonus')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_nade_bonus')

def player_spawn(event_var):
    checkBonus(event_var['userid'])

def gg_levelup(event_var):
    checkBonus(event_var['attacker'])

def checkBonus(userid):
    # Int'ify userid
    userid = int(userid)
    
    # Get player object
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Is a spectator or a bot?
    if gungamelib.isSpectator(userid) or gungamePlayer.isbot:
        return
    
    # If the weapon is a hegrenade, give them the bonus weapon
    if gungamePlayer.getWeapon() != 'hegrenade':
        return
    
    # Get bonus weapon
    bonusWeapon = gungamelib.getVariableValue('gg_nade_bonus')
    if 'weapon_' not in bonusWeapon:
        bonusWeapon = 'weapon_' + bonusWeapon
    
    # Give it and make them use it
    es.delayed('0.01', 'es_xgive %s %s' % (userid, bonusWeapon))
    es.delayed('0.02', 'es_xsexec %s "use weapon_hegrenade"' % userid)
    
def hegrenade_detonate(event_var):
    userid = event_var['userid']
    
    if not gungamelib.getPlayer(userid).isbot:
        return
    
    if gungamelib.getGlobal('isWarmup'):
        return
    
    if gungamelib.addonRegistered('gg_unl_grenade'):
        return
    
    # Get bonus weapon
    bonusWeapon = gungamelib.getVariableValue('gg_nade_bonus')
    if 'weapon_' not in bonusWeapon:
        bonusWeapon = 'weapon_' + bonusWeapon
    
    # Give it and make them use it
    es.delayed('0.01', 'es_xgive %s %s' % (userid, bonusWeapon))
    es.delayed('0.02', 'es_xsexec %s "use %s"' % (userid, bonusWeapon))
