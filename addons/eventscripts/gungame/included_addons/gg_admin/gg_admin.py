''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.285
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
info.version  = '1.0.285'
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
    gg_admin.setDisplayName('GG Admin')
    
    # Command registration
    gg_admin.registerCommand('admin', sendAdminMenu, '')
    gg_admin.registerCommand('admin_add', cmd_admin_add, '<steamid> <name> <level>')
    gg_admin.registerCommand('admin_remove', cmd_admin_remove, '<steamid>')
    gg_admin.registerCommand('admin_show', cmd_admin_show, '')
    gg_admin.registerCommand('admin_set', cmd_admin_set, '<steamid> <new level>')
    gg_admin.registerCommand('admins', cmd_admins, '')
    
    # Get admins
    adminFile = open(gungamelib.getGameDir('cfg/gungame/admins.txt'), 'r')
    
    # Format lines
    lines = map(lambda x: x.strip(), adminFile.readlines())
    lines = filter(lambda x: not x.startswith('//') and x, lines)
    
    # Close file
    adminFile.close()
    
    # Register admins
    for line in lines:
        # Fix for in-line comments
        line = line.split('//')[0]
        line = line.strip()
        
        # Get data from the line
        steamid, name, level = line.split(' ', 2)
        
        # Register them
        regAdmin(steamid, name, level)
    
    # Register commands
    cmdFile = open(gungamelib.getGameDir('cfg/gungame/admin_commands.txt'), 'r')
    
    # Format lines
    lines = map(lambda x: x.strip(), cmdFile.readlines())
    lines = filter(lambda x: not x.startswith('//') and x, lines)
    
    # Register commands
    for line in lines:
        # Fix for in-line comments
        line = line.split('//')[0]
        
        # Get data from the line
        command, level = line.split(' ', 1)
        
        # Register it
        regCmd(command, level)
    
    # Close file
    cmdFile.close()

def unload():
    # Unregister commands
    for command in dict_commands:
        es.unregsaycmd('!gg%s' % command)
        es.unregclientcmd('gg_%s' % command)
    
    # Unregister addon
    gungamelib.unregisterAddon('gg_admin')

# ==============================================================================
#   COMMANDS
# ==============================================================================
def cmd_admin_add(userid, steamid, name, level):
    # Check the admin exists
    if dict_admins.has_key(steamid):
        gungamelib.msg('gg_admin', userid, 'AdminExists', {'steamid': steamid})
        return
    
    # Open file
    adminFile = open(gungamelib.getGameDir('cfg/gungame/admins.txt'), 'a')
    
    # Write to file
    adminFile.write('\n%s %s %s\t// LOG: Added by %s <%s>\n' % (steamid, name, level, gungamelib.removeReturnChars(es.getplayername(userid)), es.getplayersteamid(userid)))
    
    # Add to admins dictionary
    dict_admins[steamid] = level
    
    # Close file
    adminFile.close()

def cmd_admin_remove(userid, steamid):
    # Check the admin exists
    if not dict_admins.has_key(steamid):
        gungamelib.msg('gg_admin', userid, 'InvalidAdmin', {'steamid': steamid})
        return
    
    # Open file and remove the line that starts with <steamid>
    adminFile = open(gungamelib.getGameDir('cfg/gungame/admins.txt'), 'r')
    lines = filter(lambda x: not x.startswith(steamid), adminFile.readlines())
    adminFile.close()
    
    # Open the file again, but write the new lines to it
    adminFile = open(gungamelib.getGameDir('cfg/gungame/admins.txt'), 'w')
    adminFile.write(''.join(lines))
    adminFile.close()
    
    # Tell them the removal was successful
    gungamelib.msg('gg_admin', userid, 'AdminRemoved', {'steamid': steamid})

def cmd_admin_show(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_admin', userid, 0, 'AdminStart')
    
    # Check the admin exists
    for steamid in dict_admins:
        level = dict_admins[steamid]
        
        gungamelib.echo('gg_admin', userid, 0, 'AdminItem', {'steamid': steamid, 'level': level})
    
    # End
    gungamelib.echo('gg_admin', userid, 0, 'AdminEnd')

def cmd_admin_set(userid, steamid, level):
    # Check the admin exists
    if not dict_admins.has_key(steamid):
        gungamelib.msg('gg_admin', userid, 'InvalidAdmin', {'steamid': steamid})
        return
    
    # Note to Devs: I will finish this off when I find a way

def cmd_admins(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_admin', userid, 0, 'AdminStart')
    
    # Get a list of active admins
    for userid in es.getUseridList():
        # Get player steamid
        steamid = es.getplayersteamid(userid)
        
        # Do they exist in the admins dictionary?
        if dict_admins.has_key(steamid):
            # Get player info
            level = dict_admins[steamid]
            name = es.getplayername(userid)
            
            # Add to console
            gungamelib.echo('gg_admin', userid, 0, 'AdminItem2', {'steamid': steamid, 'level': dict_admins[steamid], 'name': gungamelib.removeReturnChars(es.getplayername(userid))})
    
    # End
    gungamelib.echo('gg_admin', userid, 0, 'AdminEnd')

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
    menu_admin_main.addoption('commands', 'Commands')

def sendAdminMenu(userid):
    buildAdminMenu()
    popuplib.send('gg_admin_main', userid)

def selectAdminMenu(userid, choice, popupid):
    if choice == 'settings':
        sendSettingsMenu(userid)
    elif choice == 'load':
        sendAddonTypeMenu(userid)
    elif choice == 'menus':
        sendAddonMenu(userid)
    elif choice == 'commands':
        sendCommandAddonMenu(userid)

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

def setSetting(userid, args, extras):
    # Set the variable
    gungamelib.setVariableValue(extras, ' '.join(args))
    
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
#   COMMAND MENU
# ==============================================================================
def buildCommandAddonMenu(userid):
    # Get the admin level
    level = dict_admins[es.getplayersteamid(userid)]
    
    # Create menu
    menu_command = popuplib.easymenu('gg_admin_command_addon', None, selectCommandAddonMenu)
    menu_command.settitle('GG:Admin: Command addon selection')
    menu_command.setdescription('%s\n * Select an addon' % menu_command.c_beginsep)
    
    # Loop through the addons with commands
    for addonName in gungamelib.getRegisteredAddonlist():
        addonObj = gungamelib.getAddon(addonName)
        
        # Make sure this addon has commands
        if not addonObj.commands:
            continue
        
        menu_command.addoption(addonName, gungamelib.getAddonDisplayName(addonName))

def sendCommandAddonMenu(userid):
    buildCommandAddonMenu(userid)
    popuplib.send('gg_admin_command_addon', userid)

def selectCommandAddonMenu(userid, choice, popupid):
    menu_command = popuplib.easymenu('gg_admin_command', None, selectCommandMenu)
    menu_command.settitle('GG:Admin: Command menu')
    menu_command.setdescription('%s\n * Select a command' % menu_command.c_beginsep)
    
    # Get variables
    addonObj = gungamelib.getAddon(choice)
    steamid = es.getplayersteamid(userid)
    
    # Loop through the commands available for the admin
    for command in addonObj.commands:
        # Make sure the command is registered
        if command not in dict_commands:
            continue
        
        # Make sure we can run this command
        if dict_commands[command] > dict_admins[steamid]:
            continue
        
        # Add to menu
        menu_command.addoption(command, '%s %s' % (command, getCommandSyntax(command)))
    
    # Send menu
    menu_command.send(userid)

def selectCommandMenu(userid, choice, popupid):
    # Just call the command if there is no parameters
    if getCommandSyntax(choice) == '':
        callCommand(userid, choice, [])
        return
    
    # Create menu and set aesthetic things
    _input = gungamelib.EasyInput('gg_admin_command', lambda x, y, z: callCommand(x, z, y), choice)
    _input.setTitle('Call Command (%s)' % choice)
    _input.setText('Syntax: %s' % getCommandSyntax(choice))
    
    # Send menu
    _input.send(userid)

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def getCommandSyntax(command):
    for addonName in gungamelib.getRegisteredAddonlist():
        # Get the addon object
        addonObj = gungamelib.getAddon(addonName)
        
        # See if the addon has the command
        if addonObj.hasCommand(command):
            return addonObj.getCommandSyntax(command)
    
    return '<unknown>'

def getCommandsForLevel(level):
    return filter(lambda x: dict_commands[x] <= level, dict_commands)

def callCommand(userid, command, args):
    for addonName in gungamelib.getRegisteredAddonlist():
        # Get the addon object
        addonObj = gungamelib.getAddon(addonName)
        
        # See if the addon has the command
        if addonObj.hasCommand(command):
            addonObj.callCommand(command, userid, args)
            break

def cmdHandler():
    # Get command name
    name = es.getargv(0)[3:]
    
    # Call command
    callCommand(es.getcmduserid(), name, gungamelib.formatArgs())

def regAdmin(steamid, name, level):
    '''Registers an admin with group_auth and sets their permissions.'''
    # Register the admin in dict_admins
    dict_admins[steamid] = level
    
    # Create user
    es.server.queuecmd('gauth user create %s %s' % (name, steamid))
    
    # Add them to the groups
    for group in range(1, int(level)+1):
        es.server.queuecmd('gauth user join %s ggadmin%s' % (name, group))
    
    # Announce admin registration
    gungamelib.echo('gg_admin', 0, 0, 'AddedAdmin', {'name': name, 'steamid': steamid, 'level': level})

def regCmd(command, permission):
    '''Registers commands with client command and group_auth.'''
    consoleCmd = 'gg_%s' % command
    
    # Does the command exist?
    if es.exists('clientcommand', consoleCmd) or es.exists('command', consoleCmd):
        return
    
    # Does the command exist in the commands dict?
    if dict_commands.has_key(command):
        return
    
    # Add to dictionary of commands
    dict_commands[command] = int(permission)
    
    # Set group
    group = 'ggadmin%s' % permission
    
    # Create the command (say)
    es.server.queuecmd('clientcmd create say !gg%s gungame/included_addons/gg_admin/cmdHandler !gg%s #admin' % (command, command))
    es.server.queuecmd('gauth power create !gg%s 128' % command)
    es.server.queuecmd('gauth power give !gg%s %s' % (command, group))
    
    # Create the command (console)
    es.server.queuecmd('clientcmd create console gg_%s gungame/included_addons/gg_admin/cmdHandler gg_%s #admin' % (command, command))
    es.server.queuecmd('gauth power create gg_%s 128' % command)
    es.server.queuecmd('gauth power give gg_%s %s' % (command, group))
