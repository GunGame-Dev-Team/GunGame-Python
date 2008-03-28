''' (c) 2008 by the GunGame Coding Team

    Title: gg_welcome_msg
    Version: 1.0.203
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
info.version  = "1.0.203"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_welcome_msg"
info.author   = "GunGame Development Team"

def load():
    # Register addon
    gg_welcome_msg = gungamelib.registerAddon('gg_welcome_msg')
    gg_welcome_msg.setMenuText('GG Welcome Message')
    
    # Create the popup
    menuSetup()
        
def menuSetup():
    registeredAddons = gungamelib.getRegisteredAddonlist()
    registeredAddons.remove('gg_welcome_msg')
    if 'gg_warmup_round' in registeredAddons:
        registeredAddons.remove('gg_warmup_round')
    
    totalAddons = len(registeredAddons)
    totalPages = len(registeredAddons) / 10.0
    if totalPages - int(totalPages) > 0:
        totalPages = int(totalPages) + 1
    totalPages = int(totalPages)
    
    addonCounter = 0
    
    for pageNumber in range(1, totalPages + 1):
        menu = popuplib.create('welcomeMenuPage%i' % pageNumber)
        
        menu.addline('This server is running GunGame:Python (%s)' % gungame.info.version)
        if pageNumber == 1:
            menu.addline('Loaded addons:')
        else:
            menu.addline('Loaded addons (continued):')
        menu.addline('----------------------------')
        
        lineNumber = 1
        while lineNumber <= 10:
            if addonCounter < totalAddons:
                name = gungamelib.getAddonMenuText(registeredAddons[addonCounter])[3:]
                menu.addline('->%i. %s' %(addonCounter + 1, name))
            else:
                menu.addline(' ')
                
            addonCounter += 1
            lineNumber += 1
            
        menu.addline('----------------------------')
        
        if pageNumber != 1:
            if pageNumber != totalPages:
                menu.addline('->8. Previous Page')
                menu.addline('->9. Next Page')
                menu.submenu(8, 'welcomeMenuPage%i' %(pageNumber - 1))
                menu.submenu(9, 'welcomeMenuPage%i' %(pageNumber + 1))
            else:
                if totalPages > 2:
                    menu.addline('->8. Previous Page')
                    menu.addline('->9. First Page')
                    menu.submenu(8, 'welcomeMenuPage%i' %(pageNumber - 1))
                    menu.submenu(9, 'welcomeMenuPage1')
                else:
                    menu.addline('->8. First Page')
                    menu.submenu(8, 'welcomeMenuPage1')
        else:
            if totalPages > 1:
                if totalPages > 2:
                    menu.addline('->8. Last Page')
                    menu.addline('->9. Next Page')
                    menu.submenu(8, 'welcomeMenuPage%i' %totalPages)
                    menu.submenu(9, 'welcomeMenuPage%i' %(pageNumber + 1))
                else:
                    menu.addline('->9. Last Page')
                    menu.submenu(9, 'welcomeMenuPage%i' %(totalPages))
        
        menu.addline('0. Exit')

def unload():
    gungamelib.unregisterAddon('gg_welcome_msg')

def player_team(event_var):
    if event_var['disconnect'] == '0' and int(event_var['team']) > 1 and int(event_var['oldteam']) < 2:
        # Send the popup
        gamethread.delayed(2, popuplib.send, ('welcomeMenuPage1', int(event_var['userid'])))