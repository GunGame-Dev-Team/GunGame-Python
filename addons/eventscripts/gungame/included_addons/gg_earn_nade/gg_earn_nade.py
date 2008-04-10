''' (c) 2008 by the GunGame Coding Team

    Title: gg_earn_nade
    Version: 1.0.276
    Description: When a player is on "hegrenade" level and they get a kill with
                 a weapon other than an "hegrenade", they are given an
                 additional hegrenade if they do not have one.
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
info.name     = "gg_earn_nade (for GunGame: Python)"
info.version  = "1.0.276"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_earn_nade"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGamelib
    gg_earn_nade = gungamelib.registerAddon('gg_earn_nade')
    gg_earn_nade.setDisplayName('GG Earn Grenade')

def unload():
    # Unregister the addon with GunGamelib
    gungamelib.unregisterAddon('gg_earn_nade')


def player_death(event_var):
    # Get variables
    attacker = int(event_var['attacker'])
    userid = int(event_var['userid'])
    
    # Make sure that the attacker is not "world"
    if attacker == 0:
        return
    
    # Is a team-kill?
    if event_var['es_attackerteam'] == event_var['es_userteam']:
        return
    
    # Get attacker object
    gungameAttacker = gungamelib.getPlayer(attacker)
    
    # Make sure attacker's weapon is hegrenade
    if gungameAttacker.getWeapon() != 'hegrenade':
        return
    
    # Is this the warmup round?
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # Make sure the attacking weapon was not hegrenade
    if event_var['weapon'] == 'hegrenade':
        return
    
    # Get victim object
    gungameVictim = gungamelib.getPlayer(userid)
    
    # Victim is AFK?
    if gungameVictim.isPlayerAFK():
        return
    
    # Get playerlib player object
    playerlibPlayer = playerlib.getPlayer(attacker)
    
    # Only give them a hegrenade if they don't already have one
    if int(playerlibPlayer.get('he')) != 0:
        return
        
    # Check if player is a bot
    if es.isbot(attacker):
        # If the bot has a gg_nade_bonus weapon lets remove it
        nadeBonusWeapon = gungamelib.getVariableValue('gg_nade_bonus')
        if nadeBonusWeapon:
            playerlibPrimary = playerlibPlayer.get('primary')
            playerlibSecondary = playerlibPlayer.get('secondary')
            
            if nadeBonusWeapon == playerlibPrimary:
                es.server.cmd('es_xremove %d' % int(playerlibPlayer.get('weaponindex', playerlibPrimary)))
            elif nadeBonusWeapon == playerlibSecondary:
                es.server.cmd('es_xremove %d' % int(playerlibPlayer.get('weaponindex', playerlibSecondary)))
        
        es.server.cmd('es_xgive %s weapon_hegrenade' % attacker)
        es.delayed('0.01', 'es_xsexec %s "use %s"' % (attacker, 'weapon_hegrenade'))
    else:
        # Give them an additional hegrenade
        es.server.cmd('es_xgive %s weapon_hegrenade' % attacker)