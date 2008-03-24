'''
(c)2007 by the GunGame Coding Team

    Title:      gg_nade_bonus
Version #:      1.0.175
Description:    When players are on grenade level, by default, they are just given
                an hegrenade. This addon will give them an additional weapon of the
                admin's choice.
'''

# EventScripts imports
import es

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_nade_bonus Addon for GunGame: Python"
info.version  = "1.0.175"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_nade_bonus"
info.author   = "GunGame Development Team"

# Set up the bonusWeapon variable
bonusWeapon = gungamelib.getVariableValue('gg_nade_bonus')
if 'weapon_' not in gungamelib.getVariableValue('gg_nade_bonus'):
    bonusWeapon = 'weapon_' + str(bonusWeapon)

def load():
    # Register addon with gungamelib
    gg_nade_bonus = gungamelib.registerAddon('gg_nade_bonus')
    gg_nade_bonus.setMenuText('GG Nade Bonus')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_nade_bonus')

def player_spawn(event_var):
    checkBonus(event_var['userid'])

def gg_levelup(event_var):
    checkBonus(event_var['userid'])

def checkBonus(userid):
    # Int'ify userid
    userid = int(userid)
    
    # Is a spectator or a bot?
    if gungamelib.isSpectator(userid) or es.isbot(userid):
        return
    
    # Get player object
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # If the weapon is a hegrenade, give them the bonus weapon
    if gungamePlayer.getWeapon() == 'hegrenade':
        es.server.cmd('es_xdelayed 0.01 es_xgive %s %s' % (userid, bonusWeapon))
        es.server.cmd('es_xdelayed 0.02 es_xsexec %s "use weapon_hegrenade"' % userid)