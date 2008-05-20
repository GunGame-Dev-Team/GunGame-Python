''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_pro
    Version: 1.0.321
    Description: When one player knife kills another player, the attacker steals
                 a level from the victim.
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
info.name     = 'gg_knife_pro Addon for GunGame: Python'
info.version  = '1.0.321'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_knife_pro'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
proLimit = gungamelib.getVariable('gg_knife_pro_limit')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Register addon with gungamelib
    gg_knife_pro = gungamelib.registerAddon('gg_knife_pro')
    gg_knife_pro.setDisplayName('GG Knife Pro')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_pro')


def player_death(event_var):
    # ============
    # BASIC CHECKS
    # ============
    if event_var['weapon'] != 'knife':
        return
    
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # ===============
    # GET PLAYER INFO
    # ===============
    attacker = int(event_var['attacker'])
    userid = int(event_var['userid'])
    userteam = event_var['es_userteam']
    attackerteam = event_var['es_attackerteam']
    
    # =============
    # SUICIDE CHECK
    # =============
    if (attackerteam == userteam) or (userid == attacker) or (attacker == 0):
        return

    # =================
    # GET ATTACKER INFO
    # =================
    gungameAttacker = gungamelib.getPlayer(attacker)
    gungameAttackerLevel = gungameAttacker['level']
    
    # ===============
    # ATTACKER CHECKS
    # ===============
    # Fix duplicate winning
    if (gungameAttackerLevel + 1) == gungamelib.getTotalLevels():
        return
    
    # Can they levelup?
    if gungameAttacker['preventlevel'] == 1:
        gungamelib.msg('gg_knife_pro', attacker, 'AttackerPreventLevel')
        return
    
    # Is the attacker on knife or grenade level?
    if gungameAttacker.getWeapon() in ('knife', 'hegrenade'):
        gungamelib.msg('gg_knife_pro', attacker, 'CannotSkipThisLevel')
        return
    
    # ===============
    # GET VICTIM INFO
    # ===============
    gungameVictim = gungamelib.getPlayer(userid)
    gungameVictimLevel = gungameVictim['level']
    
    # =============
    # VICTIM CHECKS
    # =============
    # Can the victim level down?
    if gungameVictim['preventlevel'] == 1:
        gungamelib.msg('gg_knife_pro', attacker, 'VictimPreventLevel')
        return
    
    # Is the victim on level 1?
    if gungameVictimLevel == 1:
        gungamelib.msg('gg_knife_pro', attacker, 'VictimLevel1')
        return
    
    # Is the victim AFK?
    if gungameVictim.isPlayerAFK():
        gungamelib.msg('gg_knife_pro', attacker, 'VictimAFK')
        return
    
    # Is the level difference higher than the limit?
    if (gungameAttackerLevel - gungameVictimLevel) >= int(proLimit) and int(proLimit) != 0:
        gungamelib.msg('gg_knife_pro', attacker, 'LevelDifferenceLimit')
        return
    
    # =============
    # LEVEL CHANGES
    # =============
    # Get level info
    gungameVictimNewLevel = gungameVictimLevel - 1
    gungameAttackerNewLevel = gungameAttackerLevel + 1
    
    # Level changes
    gungamelib.triggerLevelDownEvent(userid, gungameVictimLevel, gungameVictimNewLevel, attacker, 'steal')
    gungamelib.triggerLevelUpEvent(attacker, gungameAttackerLevel, gungameAttackerNewLevel, userid, 'steal')
    
    # ===========
    # PLAY SOUNDS
    # ===========
    gungamelib.playSound(attacker, 'levelsteal')
    gungamelib.playSound(userid, 'leveldown')
    
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
    gungamelib.saytext2('gg_knife_pro', '#all', index, 'StoleLevel', {'attacker': event_var['es_attackername'], 'victim': event_var['es_username']})