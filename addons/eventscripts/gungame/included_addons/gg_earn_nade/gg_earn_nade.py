'''
(c)2007 by the GunGame Coding Team

    Title:      gg_earn_nade
Version #:      1.0.144
Description:    When a player is on "hegrenade" level and they get a kill with a weapon other than
                an "hegrenade", they are given an additional hegrenade if they do not have one.
'''

# EventScripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_earn_nade Addon for GunGame: Python"
info.version  = "1.0.144"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_earn_nade"
info.author   = "GunGame Development Team"

def load():
    # Register this addon with GunGamelib
    gg_earn_nade = gungamelib.registerAddon('gg_earn_nade')
    gg_earn_nade.setMenuText('GG Earn Grenade')

def unload():
    # Unregister the addon with GunGamelib
    gungamelib.unregisterAddon('gg_earn_nade')

def server_cvar(event_var):
    if event_var['cvarname'] == 'gg_earn_grenades' and event_var['cvarvalue'] == '0':
        es.unload('gg_earn_nade')

def player_death(event_var):
    attacker = int(event_var['attacker'])
    # Make sure that the attacker is not "world"
    if attacker != 0:
        gungameAttacker = gungamelib.getPlayer(attacker)
        # Check to see if the player is on grenade level
        if gungameAttacker.getWeapon() == 'hegrenade':
            # Make sure that PreventLevel is not set
            if gungameAttacker['preventlevel'] == 0:
                # Make sure this was not a TK
                if event_var['es_attackerteam'] != event_var['es_userteam']:
                    # Make sure the victim was not AFK
                    userid = int(event_var['userid'])
                    gungameVictim = gungamelib.getPlayer(userid)
                    if not gungameVictim.isPlayerAFK():
                        # Make sure the weapon they killed with was not an hegrenade
                        if event_var['weapon'] != 'hegrenade':
                            # Check to make sure they don't already have an hegrenade
                            playerlibPlayer = playerlib.getPlayer(attacker)
                            if int(playerlibPlayer.get('he')) == 0:
                                # Give them an additional hegrenade
                                es.server.cmd('es_xgive %d weapon_hegrenade' %attacker)