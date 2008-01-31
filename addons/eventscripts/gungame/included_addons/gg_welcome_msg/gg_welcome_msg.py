'''
(c)2007 by the GunGame Coding Team

    Title:      gg_welcome_msg
Version #:      1.0.102
Description:    This will show a simple popup message to every player that connects.
'''

# Eventscripts imports
import es
import playerlib
import gamethread
import popuplib

# Gungame import
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_welcome_msg (for GunGame: Python)"
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "GunGame Development Team"

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_welcome_msg', 'GG Welcome Message')
    
    # Create the popup
    menu = popuplib.create('gg_welcome_msg')
    menu.addline('')
    
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_welcome_msg')
    
def player_connect(event_var):
    # Send the popup in 10 seconds
    gamethread.delayed(9, popuplib.send, ('gg_welcome_msg', event_var['userid']))
    