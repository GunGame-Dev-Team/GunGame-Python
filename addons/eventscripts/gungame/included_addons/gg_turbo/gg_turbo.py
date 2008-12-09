''' (c) 2008 by the GunGame Coding Team

    Title: gg_turbo
    Version: 5.0.570
    Description: GunGame Turbo is allows players to recieve the weapon for their
                 new level immediately, instead of having to wait for the 
                 following round.
                 This addon makes the GunGame round a little more fast-paced.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import os

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
info.name     = 'gg_turbo (for GunGame5)'
info.version  = '5.0.570'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_turbo'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Console variables
gg_dead_strip = gungamelib.getVariable('gg_dead_strip')
gg_nade_bonus = gungamelib.getVariable('gg_nade_bonus')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_turbo = gungamelib.registerAddon('gg_turbo')
    gg_turbo.setDisplayName('GG Turbo')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_turbo')


def gg_levelup(event_var):
    giveNewWeapon(event_var['attacker'], event_var['old_level'], event_var['new_level'])

def gg_leveldown(event_var):
    giveNewWeapon(event_var['userid'], event_var['old_level'], event_var['new_level'])
                                   
# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def giveNewWeapon(userid, oldLevel, newLevel):
    userid = int(userid)
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if gungamelib.isDead(userid):
        return
        
    if gungamelib.isSpectator(userid):
        return
    
    if not int(gg_dead_strip):
        oldLevelWeapon = gungamelib.getLevelWeapon(oldLevel)
        newLevelWeapon = gungamelib.getLevelWeapon(newLevel)
        primaryList = gungamelib.getWeaponList('primary')
        secondaryList = gungamelib.getWeaponList('secondary')
        playerHandle = es.getplayerhandle(userid)
        
        if oldLevelWeapon in primaryList and newLevelWeapon in primaryList:
            stripWeapon(gungamePlayer, playerHandle, 'primary')
        elif oldLevelWeapon in primaryList and newLevelWeapon in ('hegrenade', 'knife'):
            if str(gg_nade_bonus) == '0':
                stripWeapon(gungamePlayer, playerHandle, 'primary')
            else:
                gungamePlayer.stripPlayer()
        elif oldLevelWeapon in secondaryList and newLevelWeapon in secondaryList:
            stripWeapon(gungamePlayer, playerHandle, 'secondary')
        elif oldLevelWeapon in secondaryList and newLevelWeapon in ('hegrenade', 'knife'):
            if str(gg_nade_bonus) == '0':
                stripWeapon(gungamePlayer, playerHandle, 'secondary')
            else:
                gungamePlayer.stripPlayer()
        else:
            gungamePlayer.stripPlayer()
        
        gungamePlayer.weaponcheck = 0
        gamethread.delayed(0.05, weaponCheck, (userid))
    
    gungamePlayer.giveWeapon()

def weaponCheck(userid):
    gungamePlayer = gungamelib.getPlayer(userid)
    if gungamePlayer.weaponcheck >= 7:
        gungamePlayer.giveWeapon()
        return
    
    gungamePlayer.weaponcheck += 1
    weapon = gungamePlayer.getWeapon()
    playerHandle = es.getplayerhandle(userid)
    
    for weaponIndex in es.createentitylist('weapon_%s' % weapon):
        if es.getindexprop(weaponIndex, 'CBaseEntity.m_hOwnerEntity') == playerHandle:
            return
    
    playerHandle = es.getplayerhandle(userid)
    weapon = gungamePlayer.getWeapon()
    
    if weapon in gungamelib.getWeaponList('primary'):
        stripWeapon(gungamePlayer, playerHandle, 'primary')
    elif weapon in gungamelib.getWeaponList('secondary'):
        stripWeapon(gungamePlayer, playerHandle, 'secondary')
    else:
        gungamePlayer.stripPlayer()
    
    gamethread.delayed(0.05, weaponCheck, (userid))

def stripWeapon(gungamePlayer, playerHandle, weaponType):
    weaponIndex = gungamePlayer.getWeaponIndex(playerHandle, weaponType)
    if weaponIndex:
        es.server.queuecmd('es_xremove %i' % weaponIndex)