''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.493
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
info.name     = 'gg_admin (for GunGame5)'
info.version  = '1.0.493'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_admin'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_settings = {}
dict_commands = {}
dict_menus = {}
dict_admins = {}
dict_cfgMenus = {}

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_admin = gungamelib.registerAddon('gg_admin')
    gg_admin.setDisplayName('GG Admin')
    gg_admin.loadTranslationFile()
    
    # Command registration
    gg_admin.registerAdminCommand('admin', sendAdminMenu, log=False, console=False)
    gg_admin.registerAdminCommand('admin_add', cmd_admin_add, '<steamid> <name> <level>')
    gg_admin.registerAdminCommand('admin_remove', cmd_admin_remove, '<steamid>')
    gg_admin.registerAdminCommand('admin_show', cmd_admin_show, log=False)
    gg_admin.registerAdminCommand('admin_set', cmd_admin_set, '<steamid> <new level>')
    gg_admin.registerAdminCommand('admins', cmd_admins, log=False)
    
    # Get admins
    lines = gungamelib.getFileLines('cfg/gungame5/admins.txt')
    
    # Register admins
    for line in lines:
        # Fix for in-line comments
        line = line.split('//')[0]
        line = line.strip()
        
        # Get data from the line
        steamid, name, level = line.split(' ', 2)
        
        # Make sure level is numerical
        if not gungamelib.isNumeric(level):
            gungamelib.echo('gg_admin', 0, 0, 'LevelNotNumeric', {'level': level})
            continue
        
        # Register them
        regAdmin(steamid, name, level)
    
    # Register commands
    lines = gungamelib.getFileLines('cfg/gungame5/admin_commands.txt')
    
    for line in lines:
        # Fix for in-line comments
        line = line.split('//')[0]
        line = line.strip()
        
        # Get data from the line
        command, level = line.split(' ', 1)
        
        # Make sure level is numerical
        if not gungamelib.isNumeric(level):
            gungamelib.echo('gg_admin', 0, 0, 'LevelNotNumeric', {'level': level})
            continue
        
        # Register it
        regCmd(command, level)
    
    # Get menu permissions
    lines = gungamelib.getFileLines('cfg/gungame5/admin_menus.txt')
    
    # Register admins
    for line in lines:
        # Fix for in-line comments
        line = line.split('//')[0]
        line = line.strip()
        
        # Get data from the line
        name, level = line.split(' ', 1)
        
        # Make sure level is numerical
        if not gungamelib.isNumeric(level):
            raise ValueError('Level (%s) is not numeric.' % level)
        
        # Register them
        dict_menus[name] = int(level)
    
    # Touch the admin log
    # Reference: http://forums.mattie.info/cs/forums/viewtopic.php?p=233366#233366
    open(gungamelib.getGameDir('addons/eventscripts/gungame/logs/adminlog.txt'), 'a').close()

def unload():
    # Unregister commands
    for command in dict_commands.copy():
        del dict_commands[command]
    
    # Unregister addon
    gungamelib.unregisterAddon('gg_admin')

# ==============================================================================
#   CONSOLE COMMANDS
# ==============================================================================
def cmd_admin_add(userid, steamid, name, level):
    # Check the admin exists
    if steamid in dict_admins:
        gungamelib.msg('gg_admin', userid, 'AdminExists', {'steamid': steamid})
        return
    
    # Create the admin
    dict_admins[steamid] = Admin(name, steamid, level)
    dict_admins[steamid].initialCreation(userid)
    
    # Tell them admin was registered
    gungamelib.msg('gg_admin', userid, 'AddedAdmin', {'steamid': steamid, 'name': name, 'level': level})

def cmd_admin_remove(userid, steamid):
    # Check the admin exists
    if steamid not in dict_admins:
        gungamelib.msg('gg_admin', userid, 'InvalidAdmin', {'steamid': steamid})
        return
    
    # Remove from admins dictionary
    dict_admins[steamid].remove()
    del dict_admins[steamid]
    
    # Tell them the removal was successful
    gungamelib.msg('gg_admin', userid, 'AdminRemoved', {'steamid': steamid})

def cmd_admin_show(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_admin', userid, 0, 'AdminStart')
    
    # Check the admin exists
    for steamid in dict_admins:
        # Get admin info
        name = dict_admins[steamid].name
        level = dict_admins[steamid].level
        
        # Echo it
        gungamelib.echo('gg_admin', userid, 0, 'AdminItem', {'name': name, 'steamid': steamid, 'level': level})
    
    # End
    gungamelib.echo('gg_admin', userid, 0, 'AdminEnd')

def cmd_admin_set(userid, steamid, level):
    # Check the admin exists
    if steamid not in dict_admins:
        gungamelib.msg('gg_admin', userid, 'InvalidAdmin', {'steamid': steamid})
        return
    
    # Set admin level
    dict_admins[steamid].setLevel(level, userid)
    
    # Tell them it was successful
    gungamelib.msg('gg_admin', userid, 'LevelSet', {'steamid': steamid, 'level': level})

def cmd_admins(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_admin', userid, 0, 'AdminStart')
    
    # Get a list of active admins
    for userid in es.getUseridList():
        # Get player steamid
        steamid = es.getplayersteamid(userid)
        
        # Do they exist in the admins dictionary?
        if steamid in dict_admins:
            # Get player info
            level = dict_admins[steamid].level
            name = gungamelib.es.getplayername(userid)
            
            # Add to console
            gungamelib.echo('gg_admin', userid, 0, 'AdminItem', {'steamid': steamid, 'level': level, 'name': name})
    
    # End
    gungamelib.echo('gg_admin', userid, 0, 'AdminEnd')

# ==============================================================================
#   ADMIN MENU
# ==============================================================================
def buildAdminMenu(userid):
    # Get admin instance
    admin = dict_admins[es.getplayersteamid(userid)]
    
    # Create main menu
    menu_admin_main = popuplib.easymenu('gg_admin_main', None, selectAdminMenu)
    menu_admin_main.settitle('GG:Admin: Admin Main Menu')
    menu_admin_main.setdescription('%s\n * Select an option...' % menu_admin_main.c_beginsep)
    
    if admin.hasLevel(dict_menus['load']):
        menu_admin_main.addoption('load', 'Load and Unload Addons')
    
    if admin.hasLevel(dict_menus['menus']):
        menu_admin_main.addoption('menus', 'Addon Menus')
    
    if admin.hasLevel(dict_menus['settings']):
        menu_admin_main.addoption('settings', 'Set Config Variables')
    
    if admin.hasLevel(dict_menus['commands']):
        menu_admin_main.addoption('commands', 'View Command List')

def sendAdminMenu(userid):
    buildAdminMenu(userid)
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
    for addon in gungamelib.getRegisteredAddonList():
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
    level = dict_admins[es.getplayersteamid(userid)].level
    
    # Create menu
    menu_command = popuplib.easymenu('gg_admin_command_addon', None, selectCommandAddonMenu)
    menu_command.settitle('GG:Admin: Command addon selection')
    menu_command.setdescription('%s\n * Select an addon' % menu_command.c_beginsep)
    
    # Loop through the addons with commands
    for addonName in gungamelib.getRegisteredAddonList():
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
    adminObj = dict_admins[steamid]
    
    # Loop through the commands available for the admin
    for command in addonObj.commands:
        # Make sure the command is registered
        if command not in dict_commands:
            continue
        
        # Make sure we can run this command
        if not adminObj.hasLevel(dict_commands[command].level):
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
    for addonName in gungamelib.getRegisteredAddonList():
        # Get the addon object
        addonObj = gungamelib.getAddon(addonName)
        
        # See if the addon has the command
        if addonObj.hasCommand(command):
            return addonObj.getCommandSyntax(command)
    
    return ''

def callCommand(userid, command, args):
    for addonName in gungamelib.getRegisteredAddonList():
        # Get the addon object
        addonObj = gungamelib.getAddon(addonName)
        
        # See if the addon has the command
        if addonObj.hasCommand(command):
            addonObj.callCommand(command, userid, args)
            break

def cmdHandler():
    # Get command name
    args = gungamelib.formatArgs()
    name = gungamelib.removeCommandPrefix(es.getargv(0))
    userid = int(es.getcmduserid())
    steamid = es.getplayersteamid(userid)
    
    # Is the user an admin?
    if steamid not in dict_admins:
        gungamelib.msg('gg_admin', userid, 'NotAdmin')
        return
    
    # Check priviledges
    if int(dict_admins[steamid]) < int(dict_commands[name]):
        gungamelib.msg('gg_admin', userid, 'InsufficientPriviledges')
        return
    
    # Call command
    callCommand(userid, name, args)

def regAdmin(steamid, name, level):
    '''Registers an admin with group_auth and sets their permissions.'''
    # Is the admin already registered?
    if steamid in dict_admins:
        return
    
    # Register the admin in dict_admins
    dict_admins[steamid] = Admin(name, steamid, level)
    
    # Announce admin registration
    gungamelib.echo('gg_admin', 0, 0, 'AddedAdmin', {'name': name, 'steamid': steamid, 'level': level})

def regCmd(command, level):
    '''Registers commands with client command and group_auth.'''
    # Does the command exist?
    if es.exists('clientcommand', 'gg_%s' % command):
        return
    
    # Does the command exist in the commands dict?
    if command in dict_commands:
        return
    
    # Register the command
    dict_commands[command] = Command(command, level)

# ==============================================================================
#   COMMAND CLASS
# ==============================================================================
class Command(object):
    def __init__(self, name, level):
        '''Initializes the command class.'''
        # Set variables
        self.level = gungamelib.clamp(level, 0, 3)
        self.name = name
        
        # Don't register command
        if self.level == 0:
            return
        
        # Create the commands
        if not es.exists('clientcommand', 'gg_%s' % self.name):
            es.regclientcmd('gg_%s' % self.name, 'gungame/included_addons/gg_admin/cmdHandler')
            es.regsaycmd(gungamelib.getSayCommandName(self.name), 'gungame/included_addons/gg_admin/cmdHandler')
    
    def __del__(self):
        '''Unregisters the say and client commands.'''
        es.unregsaycmd('%s' % gungamelib.getSayCommandName(self.name))
        es.unregclientcmd('gg_%s' % self.name)
    
    def __int__(self):
        '''int() on this object will return the level.'''
        return self.level
    
    def setLevel(self, level, setterUserid):
        '''Set the required level for this command.'''
        # Make sure level is numerical
        if not gungamelib.isNumeric(level):
            raise ValueError('Level (%s) is not numeric.' % level)
        
        # Don't change level
        if self.level == level:
            return
        
        # Re-register command
        if self.level == 0:
            es.regclientcmd('gg_%s' % self.name, 'gungame/included_addons/gg_admin/cmdHandler')
            es.regsaycmd(gungamelib.getSayCommandName(self.name), 'gungame/included_addons/gg_admin/cmdHandler')
        
        # Set level
        self.level = gungamelib.clamp(level, 0, 3)
        
        # Register command
        if self.level == 0:
            es.unregsaycmd('%s' % gungamelib.getSayCommandName(self.name))
            es.unregclientcmd('gg_%s' % self.name)
        
        # Open file, get lines then close
        commandFile = open(gungamelib.getGameDir('cfg/gungame5/admin_commands.txt'), 'r')
        lines = commandFile.readlines()
        commandFile.close()
        
        # Loop through the lines
        for line in lines:
            # Is it the line we want?
            if not line.startswith(self.name):
                continue
            
            # Get the index and set the logMessage
            index = lines.index(line)
            
            # Create log message
            if setterUserid:
                logMessage = '%s [%s]' % (gungamelib.es.getplayername(setterUserid), es.getplayersteamid(setterUserid))
            else:
                logMessage = 'CONSOLE'
            
            lines[index] = '%s %s\t// LOG: Level set by %s\n' % (self.name, self.level, logMessage)
        
        # Open the file again, but write the new lines to it
        commandFile = open(gungamelib.getGameDir('cfg/gungame5/admin_commands.txt'), 'w')
        commandFile.writelines(lines)
        commandFile.close()

# ==============================================================================
#   ADMIN CLASS
# ==============================================================================
class Admin(object):
    def __init__(self, name, steamid, level):
        '''Initializes the admin class.'''
        # Set default variables
        self.name = name
        self.steamid = steamid
        self.level = gungamelib.clamp(level, 1, 3)
    
    def initialCreation(self, setterUserid=None):
        '''Creates all the required information in the admins.txt (used to
        dynamically add admins).'''
        # Create log message
        if setterUserid:
            logMessage = '%s [%s]' % (gungamelib.es.getplayername(setterUserid), es.getplayersteamid(setterUserid))
        else:
            logMessage = 'CONSOLE'
        
        # Open file
        adminFile = open(gungamelib.getGameDir('cfg/gungame5/admins.txt'), 'a+')
        
        # Do we exist in the file?
        for line in adminFile.readlines():
            if line.startswith(self.steamid):
                raise ValueError('Cannot do initial creation for admin (%s): already exist in admins.txt' % self.steamid)
        
        # Write to file
        adminFile.write('\n%s %s %s\t// LOG: Added by %s\n' % (self.steamid, self.name, self.level, logMessage))
        
        # Close file
        adminFile.close()
    
    def __int__(self):
        return self.level
    
    def hasLevel(self, level):
        return level and self.level >= level
    
    def remove(self):
        '''Removes the admin of all priviledges.'''
        # Open file and remove the line that starts with <steamid>
        adminFile = open(gungamelib.getGameDir('cfg/gungame5/admins.txt'), 'r')
        lines = filter(lambda x: not x.startswith(self.steamid), adminFile.readlines())
        adminFile.close()
        
        # Open the file again, but write the new lines to it
        adminFile = open(gungamelib.getGameDir('cfg/gungame5/admins.txt'), 'w')
        adminFile.writelines(lines)
        adminFile.close()
    
    def setLevel(self, level, setterUserid=None):
        '''Sets the admins level.'''
        # Set level
        self.level = gungamelib.clamp(level, 1, 3)
        
        # Open file, get lines then close
        adminFile = open(gungamelib.getGameDir('cfg/gungame5/admins.txt'), 'r')
        lines = adminFile.readlines()
        adminFile.close()
        
        # Loop through the lines
        for line in lines:
            # Is it the line we want?
            if not line.startswith(self.steamid):
                continue
            
            # Get the index and set the logMessage
            index = lines.index(line)
            
            # Create log message
            if setterUserid:
                logMessage = '%s [%s]' % (gungamelib.es.getplayername(setterUserid), es.getplayersteamid(setterUserid))
            else:
                logMessage = 'CONSOLE'
            
            lines[index] = '%s %s %s\t// LOG: Level set by %s\n' % (self.steamid, self.name, self.level, logMessage)
        
        # Open the file again, but write the new lines to it
        adminFile = open(gungamelib.getGameDir('cfg/gungame5/admins.txt'), 'w')
        adminFile.writelines(lines)
        adminFile.close()