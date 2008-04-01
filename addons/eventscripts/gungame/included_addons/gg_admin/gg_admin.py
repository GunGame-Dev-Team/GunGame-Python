''' (c) 2008 by the GunGame Coding Team

    Title: gg_admin
    Version: 1.0.209
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
from gungame import gungame as gg

# ==============================================================================
#   EVENTSCRIPTS STUFF
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = "gg_admin (for GunGame: Python)"
info.version  = "1.0.209"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_admin"
info.author   = "GunGame Development Team"

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_settings = {}
dict_menus = {}
dict_commands = {}
#structure: dict_commands={'<command>': ('<type>', '<addon>', '<permission>'}
menuGGAdminMain = ' '
menuAddons = ' '
menuCFGSettingsMain = ' '

#register auth service
auth = services.use('auth')
authaddon = auth.name
if authaddon != 'group_auth':
    es.dbgmsg(0,'***** Group Auth must be loaded. Unloading GunGame.')
    es.unload('gungame')

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
    for command in dict_commands:
        es.dbgmsg(1,'*****command=%s type=%s' %(command,dict_commands[command][0]))
        if dict_commands[command][0] == 'say':
            es.unregsaycmd(command)
        else:
            es.unregclientcmd(command)
    # Unregister
    gungamelib.unregisterAddon('gg_admin')

def regCmd(type, command, function, addon, permission):
    """ 
	   Use: regCmd(type, command, function, addon, permission) 
           accepted types: say, console
           accepted permissions: admin1, admin2, admin3, user
    """
    es.dbgmsg(1,'*****regCMD')
    es.dbgmsg(1,'*****params=%s %s %s %s %s' %(type, command, function, addon, permission))	
    if type in ('say','console') and permission in ('admin1','admin2','admin3','user'):
        if type == 'console':
            temptype = 'clientcommand'
        else:
            temptype = 'saycommand'
        if es.exists(temptype, command):
            return 
        if os.path.isdir(gungamelib.getGameDir('addons/eventscripts/gungame/included_addons/%s' %addon)):
            exe = 'gungame/included_addons/%s/%s' %(addon,function)
            es.dbgmsg(1,'*****exe=%s' %exe)
        elif os.path.isdir(gungamelib.getGameDir('addons/eventscripts/gungame/custom_addons/%s' %addon)):
            exe = 'gungame/custom_addons/%s/%s' %(addon,function)
            es.dbgmsg(1,'*****exe=%s' %exe)
        else:
            es.dbgmsg(1,'*****[GunGame regCmd Error] Addon %s does not exist.' %addon)
            return
        dict_commands[command] = (type,addon,permission)
        es.dbgmsg(1,'*****dict_commands=%s' %dict_commands)
        if permission == 'user':
            level = '#IDENTIFIED'
        else:
            level = '#ADMIN'
        group = 'gg' + permission
        es.server.queuecmd('clientcmd create %s %s %s %s %s' %(type,command,exe,command,level))
        es.server.queuecmd('gauth power create %s %s' %(command,level))
        es.server.queuecmd('gauth power give %s %s' %(command,group))
		
    else:
        es.dbgmsg(0,"[Syntax Error] Accepted 'types': say, console")
        es.dbgmsg(0,"[Syntax Error] Accepted 'permissions': admin1, admin2, admin3, user")

def regMenu(menuname, displayname, addon, permission):
    if not dict_menus.has_key(menuname): 
        if type in ('admin1','admin2','admin3','user'):
            dict_menus[menuname] = displayname,addon,permission
        else:
            es.dbgmsg(0,'*****Accepted menu types- admin, user')
    else:
        es.dbgmsg(0,"*****[GunGame] The menu '%s' is already registered." %menuname) 
	
# ==============================================================================
#   MENUS SELECT 
# ==============================================================================
def selectGGAdminMain(userid, choice, popupid):
    es.dbgmsg(1,'*****selectGGAdminMain')
    if choice == 'settings':
        buildSettingsMenu(userid)
        #popuplib.send(userid, 'menuSettings')
    if choice == 'load':
        menuAddons.send(userid)
    if choice == 'menus':
        buildAddonsMenusMenu()
        #popuplib.send(userid, 'menuAddonMenus')
    if choice == 'commands':
        buildAdminCommandsMenu()
        #popuplib.send(userid, 'menuAddonMenus')

def selectLoadMenu(userid, choice, popupid):
    es.dbgmsg(1,'*****selectLoadMenu')
    es.dbgmsg(1,'*****addon=%s folder=%s action=%s' %(choice[0],choice[1],choice[2]))
    if choice[2] == 'load':
        es.dbgmsg(0,'*****load addon')
        es.load('gungame/' + choice[1] + '/' + choice[0]) 
    elif choice[2] == 'unload':
        es.dbgmsg(0,'*****unload addon')
        es.unload('gungame/' + choice[1] + '/' + choice[0])

# ==============================================================================
#   BUILD MENUS 
# ==============================================================================
def buildSettingsMenu(userid):
    es.dbgmsg(1,'*****buildSettingsMenu')
    settings = gungamelib.dict_cfgSettings
    es.dbgmsg(1,'*****settings=%s' %settings)
    menuCFGSettingsMain = popuplib.easymenu('menuCFGSettingsMain', None, buildCFGSettingsMenu)
    menuCFGSettingsMain.settitle('GG: CFG Files-\n-Select CFG file')
    for cfg in settings:
        es.dbgmsg(1,'*****cfg=%s' %cfg)
        menuCFGSettingsMain.addoption(cfg, cfg)
    menuCFGSettingsMain.send(userid)

def buildCFGSettingsMenu(userid, choice, popupid):
    es.dbgmsg(1,'*****buildCFGSettingsMenu')
    es.dbgmsg(1,'*****choice=%s' %choice)
    cfgs = gungamelib.dict_cfgSettings
    es.dbgmsg(1,'*****cfgs=%s' %cfgs)
    cfg = cfgs[choice]
    es.dbgmsg(1,'*****cfg=%s' %cfg)
    menuCFGSettings = popuplib.easymenu('menuCFGSettingsMain', None, selectCFGSetting)
    menuCFGSettings.settitle('GG: %s' %choice)
    for setting in cfg:
        es.dbgmsg(1,'*****setting=%s' %setting)
        #menuCFGSettings.addoption(setting, setting + ' ' + '=' + ' ' + str(gungamelib.getVariableValue(setting)))
        menuCFGSettings.addoption(setting, '%s = %s ' % (setting, gungamelib.getVariableValue(setting)))

    menuCFGSettings.send(userid)

def selectCFGSetting(userid, choice, popupid):
    es.dbgmsg(1,'*****selectCFGSetting')
    es.escinputbox(30,userid,'Change setting',choice,'cmdSetSetting')
    es.set('_gg_temp_setting',choice)

def setSetting():
    es.dbgmsg(1,'*****setSetting')
    setting = str(es.ServerVar('_gg_temp_setting'))
    newvalue = es.getargv(1)
    es.dbgmsg(1,'*****setting=%s oldvalue=%s' %(setting,gungamelib.getVariableValue(setting)))
    gungamelib.setVariableValue(setting,newvalue)
    es.dbgmsg(1,'*****setting=%s newvalue=%s' %(setting,gungamelib.getVariableValue(setting)))

def buildAddonsMenusMenu(userid, choice, popupid):
    es.dbgmsg(0,'*****buildAddonsMenusMenu')

def buildAdminCommandsMenu(userid, choice, popupid):
    es.dbgmsg(0,'*****buildAdminCommandsMenu')

def buildLoadMenu(userid, choice, popupid):
    es.dbgmsg(1,'*****buildLoadMenu')
    menuLoad = popuplib.easymenu('menuLoad',None,selectLoadMenu)
    es.dbgmsg(1,'*****choice=%s' %choice)
    if 'included' in choice:
        es.dbgmsg(1,'*****included_addons')
        menuLoad.settitle('GunGame Addons:\n-Select to toggle')
        list = gg.list_includedAddonsDir
        dir = 'included_addons'
        es.dbgmsg(1,'*****list=%s' %list)
    else:
        es.dbgmsg(1,'*****custom_addons')
        menuLoad.settitle('Custom Addons:\n-Select to toggle')
        list = gg.list_customAddonsDir
        dir = 'custom_addons'
        es.dbgmsg(1,'*****list=%s' %list)
    if list:
        list_registered = gungamelib.getRegisteredAddonlist()
        es.dbgmsg(1,'*****list_registered=%s' %list_registered)
        for addon in list:
                es.dbgmsg(1,'*****addon=%s' %addon)
                if addon in list_registered:
                    menuLoad.addoption((addon,dir,'unload'),addon + ' is on')
                else:
                    menuLoad.addoption((addon,dir,'load'),addon + ' is off')
        menuLoad.send(userid)					
     

# ==============================================================================
#   MISC. 
# ==============================================================================
def sendAdminMenu(userid=None):
    if not userid:
        userid = es.getcmduserid()
    menuGGAdminMain.send(userid)

def sendUserMenu(userid=None):
    es.dbgmsg(1,'*****sendUserMenu')
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
