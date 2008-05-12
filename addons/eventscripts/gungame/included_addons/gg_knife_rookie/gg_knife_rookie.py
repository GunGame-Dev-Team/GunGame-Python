''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_rookie
    Version: 1.0.316
    Description:    This is the same as gg_knife_pro, but a few small
                    differences. When one player knife kills another player,
                    the attacker will ALWAYS level up, unless on knife level.
                    The victim will always lose a level, unless the victim was
                    on level 1. Even if the victim is on level 1, the attacker
                    will gain a level.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib
import usermsg

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_knife_pro Addon for GunGame: Python"
info.version  = '1.0.316'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_knife_pro"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Register addon with gungamelib
    gg_knife_rookie = gungamelib.registerAddon('gg_knife_rookie')
    gg_knife_rookie.setDisplayName('GG Knife Rookie')
    gg_knife_rookie.addDependency('gg_knife_pro', 0)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_rookie')

def player_death(event_var):
    # Get player info
    attacker = int(event_var['attacker'])
    attackerteam = event_var['es_attackerteam']
    userid = int(event_var['userid'])
    userteam = event_var['es_userteam']
    
    # Skip if not a knife kill
    if event_var['weapon'] != 'knife':
        return
    
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # Get attacker info
    gungameAttacker = gungamelib.getPlayer(attacker)
    gungameAttackerLevel = gungameAttacker['level']
    
    # ===============
    # ATTACKER CHECKS
    # ===============
    # Check for teamkill or suicide
    if (attackerteam == userteam) or (userid == attacker) or (attacker == 0):
        return
    
    # Can they levelup anyway?
    if gungameAttacker['preventlevel'] == 1:
        gungamelib.msg('gg_knife_rookie', attacker, 'AttackerPreventLevel')
        return
    
    # Fix duplicate winning
    if gungameAttackerLevel == gungamelib.getTotalLevels():
        return
    
    # Get victim info
    gungameVictim = gungamelib.getPlayer(userid)
    gungameVictimLevel = gungameVictim['level']
    
    # Get levels
    gungameVictimNewLevel = gungameVictimLevel - 1
    gungameAttackerNewLevel = gungameAttackerLevel + 1
    
    # =============
    # VICTIM CHECKS
    # =============
    # Is the victim AFK?
    if gungameVictim.isPlayerAFK():
        gungamelib.msg('gg_knife_rookie', attacker, 'VictimAFK')
        return
    
    if gungameVictim['level'] == 1:
        gungamelib.msg('gg_knife_rookie', attacker, 'VictimLevel1')
        return
    
    if gungameVictim['preventlevel'] == 1:
        gungamelib.msg('gg_knife_rookie', attacker, 'VictimPreventLevel')
        return
    
    # =================
    # LEVEL DOWN VICTIM
    # =================
    # Trigger level down for the victim
    gungamelib.triggerLevelDownEvent(userid, gungameVictimLevel, gungameVictimNewLevel, attacker)
    
    # Play the leveldown sound
    if gungamelib.getSound('leveldown'):
        es.playsound(userid, gungamelib.getSound('leveldown'), 1.0)
    
    # =================
    # LEVEL UP ATTACKER
    # =================
    if gungameAttacker.getWeapon() == 'hegrenade':
        gungamelib.msg('gg_knife_rookie', attacker, 'AttackerNadeLevel')
    elif gungameAttacker.getWeapon() == 'knife':
        gungamelib.msg('gg_knife_rookie', attacker, 'AttackerKnifeLevel')
    else:
        # Trigger level up for the attacker
        gungamelib.triggerLevelUpEvent(attacker, gungameAttackerLevel, gungameAttackerNewLevel, userid)
    
    # =====
    # SOUND
    # =====
    if gungamelib.getSound('levelsteal'):
        es.playsound(attacker, gungamelib.getSound('levelsteal'), 1.0)
    
    # =====
    # EVENT
    # =====
    es.event('initialize', 'gg_knife_steal')
    es.event('setint', 'gg_knife_steal', 'attacker', attacker)
    es.event('setint', 'gg_knife_steal', 'attacker_level', gungameAttackerNewLevel)
    es.event('setint', 'gg_knife_steal', 'userid_level', gungameVictimNewLevel)
    es.event('setint', 'gg_knife_steal', 'userid', userid)
    es.event('fire', 'gg_knife_steal')
    
    # Announce the level stealing
    index = playerlib.getPlayer(attacker).attributes['index']
    gungamelib.saytext2('gg_knife_rookie', '#all', index, 'StoleLevel', {'attacker': event_var['es_attackername'], 'victim': event_var['es_username']})