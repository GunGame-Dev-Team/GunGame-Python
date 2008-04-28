''' (c) 2008 by the GunGame Coding Team

    Title: gg_welcome_msg
    Version: 1.0.295
    Description: Shows a simple popup message to every player that connects.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports
import time
import re

# EventScripts imports
import es
import gamethread
import playerlib
import popuplib

# GunGame imports
import gungamelib
from gungame import gungame

# ==============================================================================
#   EVENTSCRIPTS STUFF
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_welcome_msg (for GunGame: Python)'
info.version  = '1.0.295'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_welcome_msg'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_playerQueue = {}
list_rawWelcomeMsg = []
list_addonsToShow = []

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    global list_rawWelcomeMsg
    global list_addonsToShow
    
    # Register addon
    gg_welcome_msg = gungamelib.registerAddon('gg_welcome_msg')
    gg_welcome_msg.setDisplayName('GG Welcome Message')
    
    # Open file and read lines
    msgFileObj = open(gungamelib.getGameDir('cfg/gungame/welcome_msg/welcome message.txt'), 'r')
    list_rawWelcomeMsg = msgFileObj.readlines()
    msgFileObj.close()
    
    # Open addons file and read lines
    addonsFileObj = open(gungamelib.getGameDir('cfg/gungame/welcome_msg/addons.txt'), 'r')
    list_addonsToShow = addonsFileObj.readlines()
    addonsFileObj.close()
    
    # Register command
    regCmd('welcomemsg', showPopup)

def unload():
    gungamelib.unregisterAddon('gg_welcome_msg')


def player_activate(event_var):
    userid = int(event_var['userid'])
    
    if dict_playerQueue.has_key(userid):
        return
    
    # Add to the queue
    dict_playerQueue[userid] = True

def player_team(event_var):
    userid = int(event_var['userid'])
    
    # Is player disconnecting or they don't have a key?
    if event_var['disconnect'] != '0' or not dict_playerQueue.has_key(userid):
        return
    
    # Remove from queue list
    del dict_playerQueue[userid]
    
    # Send the popup
    buildMenu()
    gamethread.delayed(1, popuplib.send, ('gg_welcome_msg', userid))

# ==============================================================================
#   MENU FUNCTIONS
# ==============================================================================
def showPopup():
    # Get userid
    userid = int(es.getcmduserid())
    
    # Send popup
    buildMenu()
    popuplib.send('gg_welcome_msg', userid)

def buildMenu():
    global list_rawWelcomeMsg
    global list_addonsToShow
    
    # Get addon list
    registeredAddons = gungamelib.getRegisteredAddonlist()
    
    # Strip lines
    list_addonNames = map(lambda x: x.strip(), list_addonsToShow)
    # Filter commented blank and unregistered addons
    list_addonNames = filter(lambda x: x[:2] != '//' and x and x in registeredAddons, list_addonNames)
    # Now change each item in the list to its display name
    list_addonNames = map(lambda x: gungamelib.getAddonDisplayName(x), list_addonNames)
    
    # Loop through each line
    list_welcomeMsg = []
    for line in list_rawWelcomeMsg:
        # Strip line
        line = line.strip()
        
        # Ignore comments and skip to the next line
        if line[:2] == '//' or not line:
            continue
        
        # Replace variables
        newLine = line.replace('$version', gungame.info.version)
        newLine = newLine.replace('$author', gungame.info.author)
        newLine = newLine.replace('$date', time.strftime('%d/%m/%Y'))
        newLine = newLine.replace('$time', time.strftime('%H:%M:%S'))
        newLine = newLine.replace('$server', str(es.ServerVar('hostname')))
        
        # Replace ServerVars
        newLine = re.sub('{+(.*?)}', lambda x: str(es.ServerVar(str(x.group())[1:-1])), newLine)
        
        # Set to new line
        list_welcomeMsg.append(newLine)
    
    # Create instance and set title
    menu = popuplib.easymenu('gg_welcome_msg', None, lambda x, y, z: True)
    menu.settitle('GunGame:Python -- Welcome Message')
    menu.setdescription('%s\n%s\n%s\nThis server uses:' % (menu.c_beginsep, '\n'.join(list_welcomeMsg), menu.c_beginsep))
    
    # Add all options
    for addon in list_addonNames:
        menu.addoption(addon, addon)
    
    # Set timeout
    menuTimeout = gungamelib.getVariableValue('gg_welcome_msg_timeout')
    menu.timeout('send', menuTimeout)
    menu.timeout('view', menuTimeout)

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def regCmd(name, function):
    if es.exists('saycommand', name):
        return
        
    es.regsaycmd('!gg%s' % name, 'gungame/included_addons/gg_welcome_msg/%s' % function.__name__)
    
    if es.exists('clientcommand', name):
        return
    
    es.regclientcmd('gg_%s' % name, 'gungame/included_addons/gg_welcome_msg/%s' % function.__name__)