''' (c) 2008 by the GunGame Coding Team

    Title: gg_welcome_msg
    Version: 1.0.175
    Description: Shows a simple popup message to every player that connects.
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
info.version  = "1.0.175"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "GunGame Development Team"

def load():
    # Register addon
    gg_welcome_msg = gungamelib.registerAddon('gg_welcome_msg')
    gg_welcome_msg.setMenuText('GG Welcome Message')

def buildPopup():
    # Create the popup
    menu = popuplib.create('gg_welcome_msg')
    
    # Do header
    menu.addline('This server is running GunGame:Python (%s)' % gungame.info.version)
    menu.addline('Created by: %s' % gungame.info.author)
    menu.addline('----------------------------')
    menu.addline('->1. Loaded addons:')
    
    # Do addons
    count = 0
    for addon in gungamelib.dict_RegisteredAddons:
        # Get vars
        count += 1
        name = gungamelib.getAddonMenuText(addon)[3:]
        
        # Skip if its warmup round or welcome message
        if name == 'Warmup Round' or name == 'Welcome Message':
            continue
        
        # Do we have enough?
        if count == 10:
            menu.addline('   * ...')
            break
        
        # Add to menu
        menu.addline('   * %s' % name)
    
    # Do finishing
    menu.addline('----------------------------')
    menu.addline('0. Exit')
    menu.timeout('send', 5)
    menu.timeout('view', 5)

def player_activate(event_var):
    # Build and send popup
    buildPopup()
    gamethread.delayed(2, popuplib.send, ('gg_welcome_msg', int(event_var['userid'])))

def unload():
    gungamelib.unregisterAddon('gg_welcome_msg')