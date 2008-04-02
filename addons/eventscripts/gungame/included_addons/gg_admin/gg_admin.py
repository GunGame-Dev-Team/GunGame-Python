''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.236
    Description: Gives admins control over
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports
import os

# EventScripts imports
import es
import services
import playerlib
import popuplib

# GunGame imports
import gungamelib

# ==============================================================================
#   EVENTSCRIPTS STUFF
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = "gg_admin (for GunGame: Python)"
info.version  = '1.0.236'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_admin"
info.author   = "GunGame Development Team"

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_settings = {}
dict_menus = {}

adminMenu = None
loadMenu = None
addonMenu = None

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_admin = gungamelib.registerAddon('gg_admin')
    gg_admin.setDisplayName('GG Admin')
    
    # Create commands
    regCmd(0, '!ggadmin', sendAdminMenu)
    regCmd(1, 'gg_admin', sendAdminMenu)

def unload():
    # Unregister
    gungamelib.unregisterAddon('gg_admin')

# ==============================================================================
#   ADMIN MENU
# ==============================================================================
def buildAdminMenu():
    global adminMenu
    
    adminMenu = popuplib.easymenu('admin', None, selectAdminMenu)
    adminMenu.settitle('GG:Admin: Main Menu')
    loadMenu.setdescription('%s\n%s' % (addonMenu.c_beginsep, 'Main Admin menu.'))
    
    adminMenu.addoption('load', 'Load / Unload addons')
    adminMenu.addoption('addons', 'Addon Menus')

def sendAdminMenu(userid=None):
    global adminMenu
    
    if not userid:
        userid = es.getcmduserid()
    
    buildAdminMenu()
    adminMenu.send(userid)

def selectAdminMenu(userid, choice, popupid):
    if choice == 'addons':
        sendAddonsMenu(userid)
        return
    
    if choice == 'load':
        sendLoadMenu(userid)
        return

# ==============================================================================
#   LOAD MENU
# ==============================================================================
def buildLoadMenu():
    global loadMenu
    
    loadMenu = popuplib.easymenu('load', None, selectLoadMenu)
    loadMenu.settitle('GG:Admin: Load / Unload addons')
    loadMenu.setdescription('%s\n%s' % (addonMenu.c_beginsep, 'Load and unload addons.'))
    
    baseDir = gungamelib.getGameDir('addons/eventscripts/gungame/included_addons/')
    
    for file in os.listdir(baseDir):
        # Must be a directory
        if not os.path.isdir(baseDir + file) or not file.startswith('gg_'):
            continue
        
        # Try to get the addon
        if gungamelib.addonRegistered(file):
            state = 'LOADED'
        else:
            state = 'UNLOADED'
        
        # Add option
        loadMenu.addoption('%s|included' % file, '%s [%s]' % (file, state))
    
    baseDir = gungamelib.getGameDir('addons/eventscripts/gungame/custom_addons/')
    
    for file in os.listdir(baseDir):
        # Must be a directory
        if not os.path.isdir(baseDir + file) or not file.startswith('gg_'):
            continue
        
        # Try to get the addon
        if gungamelib.addonRegistered(file):
            state = 'LOADED'
        else:
            state = 'NOT LOADED'
        
        # Add option
        loadMenu.addoption('%s|custom' % file, '%s [%s]' % (file, state))

def selectLoadMenu(userid, choice, popupid):
    # Get type
    splitChoices = choice.split('|')
    name = splitChoices[0]
    type = splitChoices[1]
    
    # Try and get the addon
    try:
        gungamelib.getAddon(name)
        load = True
    except gungamelib.AddonError:
        load = False
    
    if load:
        es.load('gungame/%s_addons/%s' % (type, name))
    else:
        es.unload('gungame/%s_addons/%s' % (type, name))

def sendLoadMenu(userid=None):
    global loadMenu
    
    if not userid:
        userid = es.getcmduserid()
    
    buildLoadMenu()
    loadMenu.send(userid)

# ==============================================================================
#   ADDONS MENU
# ==============================================================================
def buildAddonsMenu():
    global addonMenu
    
    addonMenu = popuplib.easymenu('addon', None, selectAddonsMenu)
    addonMenu.settitle('GG:Admin: Addon Menus')
    addonMenu.setdescription('%s\n%s' % (addonMenu.c_beginsep, 'Open addon-specific menus.'))

    for addon in gungamelib.getRegisteredAddonlist():
        # Get the addon object and display name
        addonObj = gungamelib.getAddon(addon)
        addonName = gungamelib.getAddonDisplayName(addon)
        
        # Skip if the addon has no menu
        if not addonObj.hasMenu():
            continue
        
        # Add the option
        addonMenu.addoption(addon, addonName)

def selectAddonsMenu(userid, choice, popupid):
    # Get addon object
    addonObj = gungamelib.getAddon(choice)
    
    # Show menu to the selector
    addonObj.menu.send(userid)

def sendAddonsMenu(userid=None):
    global addonMenu
    
    if not userid:
        userid = es.getcmduserid()
    
    buildAddonsMenu()
    addonMenu.send(userid)

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def regCmd(type, name, function):
    if type == 0:
        if es.exists('saycommand', name):
            return
        
        es.regsaycmd(name, 'gungame/included_addons/gg_admin/%s' % function.__name__)
    elif type == 1:
        if es.exists('clientcommand', name):
            return
        
        es.regclientcmd(name, 'gungame/included_addons/gg_admin/%s' % function.__name__)