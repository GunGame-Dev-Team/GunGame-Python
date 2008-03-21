'''
(c)2007 by the GunGame Coding Team

    Title:      gg_welcome_msg
Version #:      1.0.158
Description:    This will show a simple popup message to every player that connects.
'''

# EventScripts imports
import es
import playerlib
import gamethread
import popuplib

# GunGame imports
import gungamelib
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_welcome_msg (for GunGame: Python)"
info.version  = "1.0.158"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "GunGame Development Team"

def load():
    # Register addon
    gg_welcome_msg = gungamelib.registerAddon('gg_welcome_msg')
    gg_welcome_msg.setMenuText('GG Welcome Message')
    
    # Create the popup
    menu = popuplib.create('gg_welcome_msg')
    menu.addline('This server is running GunGame:Python (%s)' % gungame.info.version)
    menu.addline('Created by: %s' % gungame.info.author)
    menu.addline('----------------------------')
    menu.addline('->1. Loaded addons:')
    
    for addon in gungamelib.dict_RegisteredAddons:
        addonObj = gungamelib.dict_RegisteredAddons[addon]
        menu.addline(' * %s' % addonObj.menuText[3:])
        
    menu.addline('----------------------------')

    menu.addline('->9. Exit')
def player_activate(event_var):
    # Send the popup
    gamethread.delayed(2, popuplib.send, ('gg_welcome_msg', int(event_var['userid'])))

def unload():
    gungamelib.unregisterAddon('gg_welcome_msg')