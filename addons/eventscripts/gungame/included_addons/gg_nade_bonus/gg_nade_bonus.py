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
#  GLOBALS
# ==============================================================================
nadeBonusWeapons = gungamelib.getVariable('gg_nade_bonus')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_nade_bonus = gungamelib.registerAddon('gg_nade_bonus')
    gg_nade_bonus.setDisplayName('GG Nade Bonus')
    gg_nade_bonus.loadTranslationFile()
    
    # Check nade bonus variable
    gamethread.delayed(0.01, checkNadeBonusVar, ())

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_nade_bonus')


def server_cvar(event_var):
    # Is it for us?
    if event_var['cvarname'] != 'gg_nade_bonus':
        return
    
    # Check nade bonus variable
    # NOTE: The delay is required just incase the event fires here before it
    #       does in gungame.py
    gamethread.delayed(0.01, checkNadeBonusVar, ())

def player_spawn(event_var):
    checkBonus(event_var['userid'])

def gg_levelup(event_var):
    checkBonus(event_var['attacker'])
    
def hegrenade_detonate(event_var):
    userid = event_var['userid']
    
    # Check the player exists
    if not gungamelib.playerExists(userid):
        return
    
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Are they a spectator?
    if gungamelib.isSpectator(userid):
        return
    
    # Are they a bot?
    if not gungamePlayer.isbot:
        return
    
    # Is it warmup?
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # Do we have unlimited grenades enabled?
    if gungamelib.addonRegistered('gg_unl_grenade'):
        return
    
    # Give bonus weapon and make them use it
    for weapon in str(nadeBonusWeapons).split(','):
        gamethread.delayed(0.01, gungamePlayer.give, (weapon, 1))
        es.delayed('0.02', 'es_xsexec %s "use %s"' % (userid, weapon))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def checkBonus(userid):
    # Int'ify userid
    userid = int(userid)
    
    # Get player object
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Are they a spectator?
    if gungamelib.isSpectator(userid):
        return
    
    # Are they a bot?
    if gungamePlayer.isbot:
        return
    
    # Check weapon
    if gungamePlayer.getWeapon() != 'hegrenade':
        return
    
    # Give bonus weapons
    for weapon in str(nadeBonusWeapons).split(','):
        gamethread.delayed(0.01, gungamePlayer.give, (weapon, 1))
    
    # Make them use their grenade
    es.delayed('0.02', 'es_xsexec %s "use weapon_hegrenade"' % userid)

def checkNadeBonusVar():
    # Helper function -- lambda isn't very readable
    def stripWeaponPrefix(text):
        if text.startswith('weapon_'):
            return text[7:]
        
        return text
    
    # We've been disabled
    if nadeBonusWeapons == '0':
        return
    
    validWeapons = []
    
    # Loop through the weapons
    for weapon in str(nadeBonusWeapons).split(','):
        # Prefix with weapon_
        if not weapon.startswith('weapon_'):
            weapon = 'weapon_%s' % weapon
        
        # Knife check
        if weapon == 'weapon_knife':
            gungamelib.echo('gg_nade_bonus', 0, 0, 'InvalidWeapon', {'weapon': 'knife'})
            continue
        
        # Check its a valid weapon
        if weapon[7:] not in gungamelib.getWeaponList('all'):
            gungamelib.echo('gg_nade_bonus', 0, 0, 'InvalidWeapon', {'weapon': weapon[7:]})
            continue
        
        # Add to the valid weapons list (without the weapon_ prefix)
        validWeapons.append(weapon[7:])
    
    # Is there any valid weapons?
    if len(validWeapons) == 0:
        gungamelib.echo('gg_nade_bonus', 0, 0, 'NoValidWeapons')
        validWeapons = ['glock']
    
    # Get old and updated variable values
    newVariableValue = ','.join(validWeapons)
    oldVariableValue = ','.join(map(stripWeaponPrefix, str(nadeBonusWeapons).split(',')))
    
    # Have the variable values even changed?
    if newVariableValue == oldVariableValue:
        return
    
    # Tell them it has changed and set the new value
    gungamelib.echo('gg_nade_bonus', 0, 0, 'NewNadeBonusWeapons', {'newValue': newVariableValue})
    gungamelib.setVariableValue('gg_nade_bonus', ','.join(validWeapons))