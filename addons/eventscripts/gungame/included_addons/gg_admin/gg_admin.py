''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.258
    Description: Gives admins control over GunGame and its addons.
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
from configobj import ConfigObj

# GunGame imports
import gungamelib
from gungame import gungame

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_admin (for GunGame: Python)'
info.version  = '1.0.258'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_admin'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_settings = {}
dict_menus = {}
dict_commands = {}
dict_admins = {}
dict_cfgMenus = {}

# ==============================================================================
#   AUTH SETUP
# ==============================================================================
try:
    # Not compatible with basic_auth
    if services.use('auth').name == 'basic_auth':
        gungamelib.echo('gg_admin', 0, 0, 'NoBasicAuth')
        es.unload('gungame/included_addons/gg_admin')
except:
    pass

# Load group auth
es.load('examples/auth/group_auth')

# Create groups
es.server.queuecmd('gauth group create ggadmin1 1')
es.server.queuecmd('gauth group create ggadmin2 1')
es.server.queuecmd('gauth group create ggadmin3 1')
es.server.queuecmd('gauth group create gguser 128')

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_admin = gungamelib.registerAddon('gg_admin')
    
    # Create commands
    regCmd('say', '!ggadmin', 'sendAdminMenu', 'gg_admin', 'admin3')
    regCmd('console', 'gg_admin', 'sendAdminMenu', 'gg_admin', 'admin3')
    regCmd('say', '!ggmenu', 'sendUserMenu', 'gg_admin' , 'user')
    
    # Get admins
    adminFile = open(gungamelib.getGameDir('cfg/gungame/admins.txt'), 'r')
    
    # Format lines
    lines = map(lambda x: x.lower().strip(), adminFile.readlines())
    lines = filter(lambda x: not x.startswith('//') and x, lines)
    
    # Register admins
    for line in lines:
        # Get data from the line
        steamid, name, level = line.split(' ', 2)
        
        # Register them
        regAdmin(steamid, name, level)

def unload():
    # Unregister commands
    for command in dict_commands:
        if dict_commands[command][0] == 'say':
            es.unregsaycmd(command)
        else:
            es.unregclientcmd(command)
    
    # Unregister addon
    gungamelib.unregisterAddon('gg_admin')

# ==============================================================================
#   ADMIN MENU
# ==============================================================================
def buildAdminMenu():
    # Create main menu
    menu_admin_main = popuplib.easymenu('gg_admin_main', None, selectAdminMenu)
    menu_admin_main.settitle('GG:Admin: Admin Main Menu')
    menu_admin_main.setdescription('%s\n * Select an option...' % menu_admin_main.c_beginsep)
    
    menu_admin_main.addoption('load', 'Load / Unload Addons')
    menu_admin_main.addoption('menus', 'Addon Menus')
    menu_admin_main.addoption('settings', 'Variable Settings')

def sendAdminMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    
    buildAdminMenu()
    popuplib.send('gg_admin_main', userid)

def selectAdminMenu(userid, choice, popupid):
    if choice == 'settings':
        sendSettingsMenu(userid)
    elif choice == 'load':
        sendAddonTypeMenu(userid)
    elif choice == 'menus':
        sendAddonMenu(userid)

# ==============================================================================
#   CFG SETTINGS MENUS 
# ==============================================================================
def buildSettingsMenu():
    # Get the configs
    configs = gungamelib.dict_cfgSettings
    
    # Create menu
    menu_cfg_settings_main = popuplib.easymenu('gg_admin_cfg_settings_main', None, buildCFGSettingsMenu)
    menu_cfg_settings_main.settitle('GG:Admin: Configs')
    menu_cfg_settings_main.setdescription('%s\n * Select a config' % menu_cfg_settings_main.c_beginsep)
    
    # Loop through each config and add it
    for config in configs:
        menu_cfg_settings_main.addoption(config, config)

def sendSettingsMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    
    buildSettingsMenu()
    popuplib.send('gg_admin_cfg_settings_main', userid)

def buildCFGSettingsMenu(userid, choice, popupid=None):
    global dict_cfgMenus
    
    # Set current menu for userid
    dict_cfgMenus[int(userid)] = choice
    
    # Get config
    config = gungamelib.dict_cfgSettings[choice]
    
    # Create menu
    menu_cfg_settings = popuplib.easymenu('gg_admin_cfg_settings', None, selectCFGSettingMenu)
    menu_cfg_settings.settitle('GG:Admin: Config setup (%s)' % choice)
    menu_cfg_settings.setdescription('%s\n * Select an option to change its value' % menu_cfg_settings.c_beginsep)
    menu_cfg_settings.submenu(0, 'gg_admin_settings')
    
    # Add the variables to the menu
    for variable in config:
        menu_cfg_settings.addoption(variable, '%s = %s ' % (variable, gungamelib.getVariableValue(variable)))
    
    # Send menu
    menu_cfg_settings.send(userid)

def selectCFGSettingMenu(userid, choice, popupid):
    # Create menu and set aesthetic things
    _input = gungamelib.EasyInput('gg_admin', setSetting, choice)
    _input.setTitle('Set setting (%s)' % choice)
    _input.setText('Enter a variable value for: %s' % choice)
    
    # Send menu
    _input.send(userid)

def setSetting(userid, choice, args):
    # Set the variable
    gungamelib.setVariableValue(args[0], choice)
    
    # Send them back to the CFG settings menu
    buildCFGSettingsMenu(userid, dict_cfgMenus[userid])

# ==============================================================================
#   ADDON TYPE MENU
# ==============================================================================
def buildAddonTypeMenu():
    # Create addons type menu
    menu_addon_type = popuplib.easymenu('gg_admin_addon_type', None, buildAddonLoad)
    menu_addon_type.settitle('GG:Admin: Addon Type Selection')
    menu_addon_type.setdescription('%s\n * Select an addon type' % menu_addon_type.c_beginsep)
    
    menu_addon_type.addoption('included', 'Included Addons')
    menu_addon_type.addoption('custom', 'Custom Addons')

def sendAddonTypeMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    
    buildAddonTypeMenu()
    popuplib.send('gg_admin_addon_type', userid)

# ==============================================================================
#   LOAD MENU
# ==============================================================================
def buildAddonLoad(userid, choice, popupid):
    # Create menu
    menu_load = popuplib.easymenu('gg_admin_addon_load', None, selectAddonLoad)
    menu_load.settitle('GG:Admin: Addon Load Menu')
    menu_load.setdescription('%s\n * Select to toggle' % menu_load.c_beginsep)
    
    if choice == 'included':
        # Get included addons list
        addons = gungame.list_includedAddonsDir
        type = 'included'
    else:
        # Get custom addon list
        addons = gungame.list_customAddonsDir
        type = 'custom'
    
    # Loop through the addons
    for item in addons:
        if gungamelib.addonRegistered(item):
            menu_load.addoption((item, type, 'unload'), '%s is on' % item)
        else:
            menu_load.addoption((item, type, 'load'), '%s is off' % item)
    
    # Send menu
    menu_load.send(userid)

def selectAddonLoad(userid, choice, popupid):
    if choice[2] == 'unload':
        es.unload('gungame/%s_addons/%s' % (choice[1], choice[0]))
    else:
        es.load('gungame/%s_addons/%s' % (choice[1], choice[0]))

# ==============================================================================
#   ADDON MENUS
# ==============================================================================
def buildAddonMenu():
    # Create menu
    menu_addon_menu = popuplib.easymenu('gg_admin_addon', None, selectAddonMenu)
    menu_addon_menu.settitle('GG:Admin: Addon Menus')
    menu_addon_menu.setdescription('%s\n * Open addon-specific menus' % menu_addon_menu.c_beginsep)
    
    # Loop through the addons
    for addon in gungamelib.getRegisteredAddonlist():
        # Get the addon object and display name
        addonObj = gungamelib.getAddon(addon)
        addonName = gungamelib.getAddonDisplayName(addon)
        
        # Skip if the addon has no menu
        if not addonObj.hasMenu():
            continue
        
        # Add the option
        menu_addon_menu.addoption(addon, addonName)

def sendAddonMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    
    buildAddonMenu()
    popuplib.send('gg_admin_addon', userid)

def selectAddonMenu(userid, choice, popupid):
    # Get addon object
    addonObj = gungamelib.getAddon(choice)
    
    # Send the menu
    addonObj.sendMenu(userid)

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def regAdmin(steamid, name, level):
    '''Registers an admin with group_auth and sets their permissions.'''
    # NOTE TO HTP: If you want an admins dictionary, just uncomment the next line.
    # dict_admins[name] = steamid, level
    
    # Create user
    es.server.queuecmd('gauth user create %s %s' % (name, steamid))
    
    # Add them to the groups
    for group in range(1, int(level)+1):
        es.server.queuecmd('gauth user join %s ggadmin%s' % (name, group))

def regCmd(type, command, block, addon, permission):
    ''' types: say, console
        permissions: admin1, admin2, admin3, user
    '''
    
    # Correct type
    if type not in ('say', 'console'):
        gungamelib.echo('gg_admin', 0, 0, 'InvalidType', {'command': command, 'type': type})
        return
    
    # Correct permission
    if permission not in ('admin1', 'admin2', 'admin3', 'user'):
        gungamelib.echo('gg_admin', 0, 0, 'InvalidPermission', {'command': command, 'permission': permission})
        return
    
    # Set type
    temptype = 'clientcommand' if type == 'console' else 'saycommand'
    
    # Does the command exist?
    if es.exists(temptype, command):
        return
    
    # Does the addon exist?
    if not gungamelib.addonExists(addon):
        gungamelib.echo('gg_admin', 0, 0, 'AddonNotExist', {'command': command, 'addon': addon})
        return
    
    # Set addon block
    addonblock = 'gungame/%s/%s/%s' % ('custom_addons' if gungamelib.getAddonType(addon) else 'included_addons', addon, block)
    
    # Add to command dictionary
    if not dict_commands.has_key(command):
        # Add to dictionary of commands
        dict_commands[command] = type, addon, permission
        
        # Set level and group variables
        level = '#ALL' if permission == 'user' else '#ADMIN'
        levelNum = 128 if permission == 'user' else 1
        group = 'gg' + permission
        
        # Create the command
        es.server.queuecmd('clientcmd create %s %s %s %s %s' % (type, command, addonblock, command, level))
        es.server.queuecmd('gauth power create %s %s' % (command, levelNum))
        es.server.queuecmd('gauth power give %s %s' % (command, group))