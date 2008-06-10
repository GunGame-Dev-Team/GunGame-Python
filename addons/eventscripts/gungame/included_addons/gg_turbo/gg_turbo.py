''' (c) 2008 by the GunGame Coding Team

    Title: gg_turbo
    Version: 1.0.344
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
info.name     = 'gg_turbo Addon for GunGame: Python'
info.version  = '1.0.344'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_turbo'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_turbo = gungamelib.registerAddon('gg_turbo')
    gg_turbo.setDisplayName('GG Turbo')
    gg_turbo.addDependency('gg_dead_strip', 1)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_turbo')


def gg_levelup(event_var):
    giveNewWeapon(event_var['attacker'])

def gg_leveldown(event_var):
    giveNewWeapon(event_var['userid'])

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def giveNewWeapon(userid):
    userid = int(userid)
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if gungamelib.isDead(userid):
        return
        
    if gungamelib.isSpectator(userid):
        return
    
    if gungamePlayer.getWeapon() == 'knife':
        es.sexec(userid, 'use weapon_knife')
    
    gungamePlayer.stripPlayer()
    
    # Only delay if we are on linux
    if os.name == 'posix':
        gamethread.delayed(0.01, delayedGiveNewWeapon, (userid))
    else:
        gungamePlayer.giveWeapon()
        
 def delayedGiveNewWeapon(userid):
    if gungamelib.isDead(userid):
        return
        
    if gungamelib.isSpectator(userid):
        return
        
    gungamePlayer = gungamelib.getPlayer(userid)
    gungamePlayer.giveWeapon()