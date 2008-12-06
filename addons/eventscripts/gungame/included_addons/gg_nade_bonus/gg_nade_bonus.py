''' (c) 2008 by the GunGame Coding Team

    Title: gg_nade_bonus
    Version: 5.0.559
    Description: When players are on grenade level, by default, they are just given
                 an hegrenade. This addon will give them an additional weapon of the
                 admin's choice.
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
info.name     = 'gg_nade_bonus (for GunGame5)'
info.version  = '5.0.559'
info.url      = 'http://gungame5.com/'
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
    giveBonusWeapons(event_var['userid'])

def gg_levelup(event_var):
    giveBonusWeapons(event_var['attacker'])

def hegrenade_detonate(event_var):
    # NOTE TO DEVS: Don't know whether I recoded this right... I don't
    #               understand what it does.
    
    userid = event_var['userid']
    
    gungamePlayer = gungamelib.getPlayer(userid)
    if not gungamePlayer.isbot:
        return
    
    if gungamelib.getGlobal('isWarmup'):
        return
    
    if gungamelib.addonRegistered('gg_unl_grenade'):
        return
    
    # Use bonus weapons
    for weapon in gungamelib.getVariableValue('gg_nade_bonus').split(','):
        # Prefix with weapon_
        if not weapon.startswith('weapon_'):
            weapon = 'weapon_%s' % weapon
        
        if weapon == 'weapon_knife':
            # TODO: [see comment below]
            continue
        
        if weapon[7:] not in gungamelib.getWeaponList('all'):
            # TODO: Add warning message. Preferably not here but when the value
            #       is changed in server_cvar?
            continue
        
        # Make them use it
        es.delayed('0.02', 'es_xsexec %s "use %s"' % (userid, weapon))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def giveBonusWeapons(userid):
    # Int'ify userid
    userid = int(userid)
    
    # Get player object
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Is a spectator or a bot?
    if gungamelib.isSpectator(userid) or gungamePlayer.isbot:
        # NOTE TO DEVS: Why are we not giving nade bonus weapons to bots?
        return
    
    # If the weapon is a hegrenade, give them the bonus weapon
    if gungamePlayer.getWeapon() != 'hegrenade':
        return
    
    # Give bonus weapons
    for weapon in gungamelib.getVariableValue('gg_nade_bonus').split(','):
        # Prefix with weapon_
        if not weapon.startswith('weapon_'):
            weapon = 'weapon_%s' % weapon
        
        if weapon == 'weapon_knife':
            # TODO: [see comment below]
            continue
        
        if weapon[7:] not in gungamelib.getWeaponList('all'):
            # TODO: Add warning message. Preferably not here but when the value
            #       is changed in server_cvar?
            continue
        
        # Give them the weapon
        gamethread.delayed(0.01, gungamePlayer.give, (weapon, 1))
    
    # Give it and make them use it
    es.delayed('0.02', 'es_xsexec %s "use weapon_hegrenade"' % userid)