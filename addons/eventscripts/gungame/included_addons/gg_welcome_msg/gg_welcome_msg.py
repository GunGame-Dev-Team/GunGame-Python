#!/usr/bin/env python
'''
================================================================================
    All content copyright (c) 2008, GunGame Coding Team
================================================================================
    Name: gg_welcome_msg
    Main Author: Saul Rennison
    Version: 1.0.0 (12.01.2008)
================================================================================
    This will show a simple popup message to every player that connects.
================================================================================
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
info.version  = "1.0.0"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "Saul (cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008)"

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_welcome_msg', 'GG Welcome Message')
    
    # Create the popup
    menu = popuplib.create('gg_welcome_msg')
    menu.addline('')
    
def player_connect(event_var):
    # Send the popup in 10 seconds
    gamethread.delayed(9, popuplib.send, ('gg_welcome_msg', event_var['userid']))
    