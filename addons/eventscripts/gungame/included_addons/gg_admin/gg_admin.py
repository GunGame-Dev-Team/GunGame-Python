'''
(c)2007 by the GunGame Coding Team

    Title:      gg_admin
Version #:      1.0.155
Description:    Gives menu based admin control of gungame and it's addons.
'''

# Python imports
import os

# EventScripts imports
import es
import services
import playerlib
import popuplib

# GunGame imports
import gungamelib as gga

info = es.AddonInfo()
info.name     = "gg_admin (for GunGame: Python)"
info.version  = "1.0.155"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_admin"
info.author   = "GunGame Development Team"

# This will hold all settings not including "addon toggles"
dict_cfgSettings = {}
# This holds registered menu info
dict_menus = {}

auth = services.use('auth')

#dict_gungameVariables, dict_gungameRegisteredAddons, list_includedAddonsDir, list_customAddonsDir


def load():
    es.dbgmsg(0,'*****load')
    global adminmenu
    auth.registerCapability('!ggadmin', auth.ADMIN)
    if not es.exists('saycommand', '!ggadmin'):
        es.regsaycmd('!ggadmin', 'gungame/included_addons/gg_admin/sendAdminMenu')
    if not es.exists('saycommand', '!gguser'):
        es.regsaycmd('!gguser', 'gungame/included_addons/gg_admin/sendUserMenu')
    if not es.exists('clientcommand', '!set_setting'):
        es.regclientcmd('!set_setting', 'gungame/included_addons/gg_admin/set_setting')
    
    gga.registerAddon('gungame/included_addons/gg_admin', 'GG Admin')
    regMenu('settingsmenu','GG Settings','admin','gg_admin')
    regMenu('defaultaddons','GG Included Addons','admin','gg_admin')
    regMenu('customaddons','GG Custom Addons','admin','gg_admin')

def unload():
    gga.unregisterAddon('gungame/included_addons/gg_admin', 'GG Admin')
    es.unregsaycmd('!ggadmin')
    es.unregsaycmd('!gguser')
    es.unregclientcmd('!set_setting') 

def regMenu(menuname,displayname,type,addon):
    es.dbgmsg(0,'*****regMenu')
    es.dbgmsg(0,'*****menuname=%s displayname=%s type=%s addon=%s' %(menuname,displayname,type,addon))
    
    # types- admin, user
    # gg_regMenu('mymenu','My Menu','admin','myaddon')
    if not dict_menus.has_key(menuname): 
        if type in ('admin','user'):
            dict_menus[menuname] = displayname,type,addon
        else:
            es.dbgmsg(0,'*****Accepted menu types- admin, user')
    else:
        es.dbgmsg(0,'*****That menu is already registered.')

def buildAdminMenu(userid):
    es.dbgmsg(0,'*****buildAdminMenu')
    global adminmenu
    adminmenu = popuplib.easymenu('adminmenu'+ str(userid),None,selectAdminMenu)
    adminmenu.settitle('GunGame Admin Menu')
    for menu in dict_menus:
        es.dbgmsg(0,'*****menuname=%s displayname=%s type=%s addon=%s' %(menu,dict_menus[menu][0],dict_menus[menu][1],dict_menus[menu][2]))      
        if dict_menus[menu][1] == 'admin':
            es.dbgmsg(0,'*****menu= %s' %menu)
            adminmenu.addoption(menu,dict_menus[menu][0])

def buildUserMenu(userid):
    es.dbgmsg(0,'*****buildUserMenu')
    global usermenu
    usermenu = popuplib.easymenu('usermenu'+ str(userid),None,selectUserMenu)
    usermenu.settitle('GunGame User Menu')
    for menu in dict_menus:
        es.dbgmsg(0,'*****menuname=%s displayname=%s type=%s addon=%s' %(menu,dict_menus[menu][0],dict_menus[menu][1],dict_menus[menu][2]))      
        if dict_menus[menu][1] == 'user':
            es.dbgmsg(0,'*****menu= %s' %menu)
            usermenu.addoption(menu,dict_menus[menu][0])

def sendAdminMenu():
    userid = es.getcmduserid()
    if auth.isUseridAuthorized(userid, '!ggadmin'):
        if int(popuplib.exists('adminmenu' + str(userid))):
            popuplib.delete('adminmenu' + str(userid))
        buildAdminMenu(userid)
        adminmenu.send(userid)
    else:
        es.tell(userid,'#multi','#green[GunGame Admin]#lightgreen You do not have permission for that command.')

def sendUserMenu():
    userid = es.getcmduserid()
    if int(popuplib.exists('usermenu' + str(userid))):
        popuplib.delete('usermenu' + str(userid))
    buildUserMenu(userid)
    usermenu.send(userid)        

def selectAdminMenu(userid,choice,popupid):
    es.dbgmsg(0,'*****selectAdminMenu')
    popuplib.delete('adminmenu' + str(userid))
    if choice == 'settingsmenu':
        buildSettingsMenu()            
    if choice in ('defaultaddons','customaddons'):
        buildAddonsMenu(choice,userid)
        choice = 'addonsmenu'                  
    popuplib.send(choice,userid)

def selectUserMenu(userid,choice,popupid):
    es.dbgmsg(0,'*****selectUserMenu')
    popuplib.delete('usermenu' + str(userid))
    popuplib.send(choice,userid)

def buildSettingsMenu():
    global settingsmenu
    es.dbgmsg(0,'*****adminmenu_settings')
    if int(popuplib.exists('settingsmenu')):
        popuplib.delete('settingsmenu')
    settingsmenu = popuplib.easymenu('settingsmenu',None,_setting_select)
    settingsmenu.settitle('GunGame Settings:\n-Select to change')    
    for setting in gga.dict_cfgSettings:
        es.dbgmsg(0,'*****setting=%s value= %s' %(setting,str(gga.gungamelib.getVariableValue(setting))))
        settingsmenu.addoption(setting, setting + ' ' + str(gga.gungamelib.getVariableValue(setting)))

def _setting_select(userid,choice,popupid):
    es.dbgmsg(0,'*****_setting_select')
    es.escinputbox(30,userid,'Change setting',choice,'!set_setting')
    es.set('_gg_temp_setting',choice)

def set_setting():
    es.dbgmsg(0,'*****set_setting')
    setting = str(es.ServerVar('_gg_temp_setting'))
    newvalue = es.getargv(1)
    es.dbgmsg(0,'*****setting=%s newvalue=%s' %(setting,es.getargv(1)))
    gga.gungamelib.setVariableValue(setting,newvalue)
    gga.dict_cfgSettings[setting] = newvalue

def buildAddonsMenu(type,userid):
    es.dbgmsg(0,'*****buildAddonsMenu')
    global addonsmenu
    addonsmenu = popuplib.easymenu('addonsmenu',None,_addons_select)
    if type == 'defaultaddons':
        addonsmenu.settitle('GunGame Addons:\n-Select to toggle')
        for addon in gga.list_includedAddonsDir:
            es.dbgmsg(0,'*****addon=%s' %addon)
            if int(gga.checkRegisteredAddon('gungame/included_addons/'+ addon)):
                addonsmenu.addoption((addon,'included_addons','unload'),addon + ' is on')
            else:
                addonsmenu.addoption((addon,'included_addons','load'),addon + ' is off')           
    elif type == 'customaddons':
        addonsmenu.settitle('Custom Addons:\n-Select to toggle')
        if gga.list_customAddonsDir:
            for addon in gga.list_customAddonsDir:
                es.dbgmsg(0,'*****addon=%s' %addon)
                if int(gga.checkRegisteredAddon('gungame/custom_addons/'+ addon)):
                    addonsmenu.addoption((addon,'custom_addons','unload'),addon + ' is on')
                else:
                    addonsmenu.addoption((addon,'custom_addons','load'),addon + ' is off')
        else:
            es.tell(userid,'There are no custom addons.')

def _addons_select(userid,choice,popupid):
    es.dbgmsg(0,'*****_addons_select')
    es.dbgmsg(0,'*****addon=%s type=%s action=%s' %(choice[0],choice[1],choice[2]))
    if choice[2] == 'load':
        es.dbgmsg(0,'*****load addon')
        es.load('gungame/' + choice[1] + '/' + choice[0]) 
    elif choice[2] == 'unload':
        es.dbgmsg(0,'*****unload addon')
        es.unload('gungame/' + choice[1] + '/' + choice[0])
