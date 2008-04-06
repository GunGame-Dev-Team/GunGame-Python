''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.255
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
from configobj import ConfigObj

# GunGame imports
import gungamelib
from gungame import gungame as gg

# ==============================================================================
#   EVENTSCRIPTS STUFF
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = "gg_admin (for GunGame: Python)"
info.version  = "1.0.254"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_admin"
info.author   = "GunGame Development Team"

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_settings = {}
dict_menus = {}
dict_commands = {}

#  auth stuff
try:
    auth = services.use('auth')
    if auth.name == 'basic_auth':
        es.dbgmsg(0,'*****basic_auth must not be loaded when using gg_admin.')
        es.unload('gungame/included_addons/gg_admin')
except:
    pass
es.load('examples/auth/group_auth')

#get admins
gameDir = es.ServerVar('eventscripts_gamedir')
adminfile = gameDir + '/cfg/gungame/gg_admins.ini'
dict_ggAdmins = ConfigObj(adminfile)

menuGGAdminMain = ' '
menuAddons = ' '
menuCFGSettingsMain = ' '

#setup group_auth
es.server.queuecmd('gauth group create ggadmin1 1')
es.server.queuecmd('gauth group create ggadmin2 1')
es.server.queuecmd('gauth group create ggadmin3 1')
es.server.queuecmd('gauth group create gguser 128')

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    global menuGGAdminMain, menuAddons
    # Register
    gg_admin = gungamelib.registerAddon('gg_admin')
	
    # Create commands
    # regCmd(type, command, function, addon, permission) 
    regCmd('say', '!ggadmin', 'sendAdminMenu', 'gg_admin', 'admin3')
    regCmd('console', 'gg_admin', 'sendAdminMenu', 'gg_admin', 'admin3')
    regCmd('say', '!ggmenu', 'sendUserMenu', 'gg_admin' , 'user')

    #internal cmd to set cfg setting, called when escinput box used
    if not int(es.exists('clientcommand','cmdSetSetting')):
        es.regclientcmd('cmdSetSetting','gungame/included_addons/gg_admin/setSetting', 'Set CFG setting')

    #register our admins here
    for admin in dict_ggAdmins['GGAdmins']:
        regAdmin(admin,dict_ggAdmins['GGAdmins'][admin])

    menuGGAdminMain = popuplib.easymenu('menuGGAdminMain', None, selectGGAdminMain)
    menuGGAdminMain.settitle('GG: Admin')    
    menuGGAdminMain.addoption('load', 'Load / Unload addons')
    menuGGAdminMain.addoption('settings', 'Addon Settings')
    menuGGAdminMain.addoption('menus', 'Addon Menus')
    menuGGAdminMain.addoption('commands', 'Commands')

    menuAddons = popuplib.easymenu('menuAddons', None, buildLoadMenu)
    menuAddons.settitle('GG: Addons Main')
    menuAddons.addoption('list_includedAddonsDir', 'GG Addons')
    menuAddons.addoption('list_customAddonsDir', 'Custom Addons')

def unload():
    # let's be kind and unregister commands
    for command in dict_commands:
        if dict_commands[command][0] == 'say':
            es.unregsaycmd(command)
        else:
            es.unregclientcmd(command)
    # Unregister
    gungamelib.unregisterAddon('gg_admin')

def regAdmin(admin,data):
    # Register an admin and set his permission groups
    data = data.split()
    es.server.queuecmd('gauth user create %s %s' %(data[0],admin))
    for group in range(1,int(data[1])+1):
        es.server.queuecmd('gauth user join %s ggadmin%s' %(data[0],group))

def regCmd(type, command, function, addon, permission):
    """ 
	   Use: regCmd(type, command, function, addon, permission) 
           accepted types: say, console
           accepted permissions: admin1, admin2, admin3, user
    """
	
    #check for accepted 'type' and 'permission'	
    if type in ('say','console') and permission in ('admin1','admin2','admin3','user'):
        # get the command type
        if type == 'console':
            temptype = 'clientcommand'
        else:
            temptype = 'saycommand'

        # if the command already exists don't register it
        if es.exists(temptype, command):
            return 

        #  get the addon path to complete the execution function
        #is it an included_addon?
        if os.path.isdir(gungamelib.getGameDir('addons/eventscripts/gungame/included_addons/%s' %addon)):
            exe = 'gungame/included_addons/%s/%s' %(addon,function)
        #or is it a custom_addon?			
        elif os.path.isdir(gungamelib.getGameDir('addons/eventscripts/gungame/custom_addons/%s' %addon)):
            exe = 'gungame/custom_addons/%s/%s' %(addon,function)
        # evidentally the scripter mistyped his addon name... oops
        else:
            es.dbgmsg(0,'*****[GunGame regCmd Error] Addon %s does not exist.' %addon)
            return

        # now let's add it to our dictionary for later use,
        # but we wouldn't want to add it if it's already there, now would we?
        if not dict_commands.has_key(command):
            dict_commands[command] = (type,addon,permission)
            es.dbgmsg(1,'*****dict_commands=%s' %dict_commands)

            # Finally, it's time to register the command with group_auth and assign it to it's proper group
            if permission == 'user':
                level = '#ALL'
                intlevel = 128
            else:
                level = '#ADMIN'
                intlevel = 1
            group = 'gg' + permission
            es.server.queuecmd('clientcmd create %s %s %s %s %s' %(type,command,exe,command,level))
            es.server.queuecmd('gauth power create %s %s' %(command,intlevel))
            es.server.queuecmd('gauth power give %s %s' %(command,group))
		
    else:
        es.dbgmsg(0,"[Syntax Error] Accepted 'types': say, console")
        es.dbgmsg(0,"[Syntax Error] Accepted 'permissions': admin1, admin2, admin3, user")	
	
# ==============================================================================
#   MENU SELECT for Main Admin Menu
# ==============================================================================
def selectGGAdminMain(userid, choice, popupid):
    if choice == 'settings':
        buildSettingsMenu(userid)
    if choice == 'load':
        menuAddons.send(userid)
    if choice == 'menus':
        buildAddonsMenusMenu(userid)
    if choice == 'commands':
        buildAdminCommandsMenu(userid)

# ==============================================================================
#   CFG SETTINGS MENUS 
# ==============================================================================
def buildSettingsMenu(userid):
    #get the dictionary of the various cfg file settings
    settings = gungamelib.dict_cfgSettings
    menuCFGSettingsMain = popuplib.easymenu('menuCFGSettingsMain', None, buildCFGSettingsMenu)
    menuCFGSettingsMain.settitle('GG: CFG Files-\n-Select CFG file')
    #add the various cfg file names to the menu
    for cfg in settings:
        menuCFGSettingsMain.addoption(cfg, cfg)
    menuCFGSettingsMain.send(userid)

def buildCFGSettingsMenu(userid, choice, popupid=None):
    
    global activecfgmenu
    activecfgmenu = choice
    
    #get the dictionary of the various cfg file settings
    cfgs = gungamelib.dict_cfgSettings

    #get the specific cfg file settings
    cfg = cfgs[choice]
    menuCFGSettings = popuplib.easymenu('menuCFGSettings', None, selectCFGSetting)
    menuCFGSettings.settitle('GG: %s' %choice)
    menuCFGSettings.submenu(0,'menuCFGSettingsMain')
    #add the cfg files' settings to the menu
    for setting in cfg:
        menuCFGSettings.addoption(setting, '%s = %s ' % (setting, gungamelib.getVariableValue(setting)))
    menuCFGSettings.send(userid)

def selectCFGSetting(userid, choice, popupid):
    es.escinputbox(30,userid,'Change setting',choice,'cmdSetSetting')

    #set this to the name of the variable we are going to change, it's used in setSetting
    global tempsetting
    tempsetting = choice

def setSetting():
	
    global activecfgmenu, tempsetting
    userid = es.getcmduserid()

    #get the new value
    newvalue = es.getargv(1)

    #set the variable
    gungamelib.setVariableValue(tempsetting,newvalue)
	
    # Now let's return them to their previos menu
    buildCFGSettingsMenu(userid,activecfgmenu)
    
# ==============================================================================
#   ADDONS MENUS MENU
# ==============================================================================
def buildAddonsMenusMenu(userid):

    menuAddonsMenus = popuplib.easymenu('menuAddonsMenus', None, selectAddonsMenu)
    menuAddonsMenus.settitle('GG:Admin: Addon Menus')
    menuAddonsMenus.setdescription('%s\n%s' % (menuAddonsMenus.c_beginsep, 'Open addon-specific menus.'))
    
    loopcount = False
    for addon in gungamelib.getRegisteredAddonlist():
        # Get the addon object and display name
        addonObj = gungamelib.getAddon(addon)
        addonName = gungamelib.getAddonDisplayName(addon)
        
        # Skip if the addon has no menu
        if not addonObj.hasMenu():
            continue
        
        # Add the option
        menuAddonsMenus.addoption(addon, addonName)
        loopcount = True
    
	# Make sure there's options on the menu, we don't want to send an empty menu.
    if loopcount:
        menuAddonsMenus.send(userid)
    else:
        #gungamelib.msg('gg_admin', userid, string, tokens={}, showPrefix=True):
        es.tell(userid, 'There are no registered addon menus.')

def selectAddonsMenu(userid, choice, popupid):
    # Get addon object
    addonObj = gungamelib.getAddon(choice)
    
    # Show menu to the selector
    addonObj.menu.send(userid)

def buildAdminCommandsMenu(userid, choice, popupid):
    es.dbgmsg(0,'*****buildAdminCommandsMenu')

# ==============================================================================
#   ADDONS LOAD/UNLOAD MENU
# ==============================================================================
def buildLoadMenu(userid, choice, popupid):
    menuLoad = popuplib.easymenu('menuLoad',None,selectLoadMenu)
    if 'included' in choice:
        menuLoad.settitle('GunGame Addons:\n-Select to toggle')
        list = gg.list_includedAddonsDir
        dir = 'included_addons'
    else:
        menuLoad.settitle('Custom Addons:\n-Select to toggle')
        list = gg.list_customAddonsDir
        dir = 'custom_addons'
    if list:
        list_registered = gungamelib.getRegisteredAddonlist()
        for addon in list:
                if addon != 'gg_admin':
                    if addon in list_registered:
                        menuLoad.addoption((addon,dir,'unload'),addon + ' is on')
                    else:
                        menuLoad.addoption((addon,dir,'load'),addon + ' is off')
		menuLoad.submenu(0,'menuAddons')
        menuLoad.send(userid)					
     
def selectLoadMenu(userid, choice, popupid):
    #load/unload addon
    if choice[2] == 'load':
        es.load('gungame/' + choice[1] + '/' + choice[0]) 
    elif choice[2] == 'unload':
        es.unload('gungame/' + choice[1] + '/' + choice[0])
    menuAddons.send(userid)

# ==============================================================================
#   MISC. 
# ==============================================================================
def sendAdminMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    menuGGAdminMain.send(userid)

def sendUserMenu(userid=None):
    es.dbgmsg(1,'*****sendUserMenu')
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
