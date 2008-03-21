'''
(c)2007 by the GunGame Coding Team

    Title:      gg_welcome_msg
Version #:      1.0.155
Description:    This will show a simple popup message to every player that connects.
'''

# EventScripts imports
import es
import playerlib
import gamethread
import popuplib

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_welcome_msg (for GunGame: Python)"
info.version  = "1.0.155"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "GunGame Development Team"

def load():
    # Register addon with gungamelib
    gg_welcome_msg = gungamelib.registerAddon('gg_welcome_msg')
    gg_welcome_msg.setMenuText('GG Welcome Message')
    
    # Create the popup
    menu = popuplib.create('gg_welcome_msg')
    menu.addline('')
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_welcome_msg')
    
def player_connect(event_var):
    # Send the popup in 10 seconds
    gamethread.delayed(9, popuplib.send, ('gg_welcome_msg', event_var['userid']))