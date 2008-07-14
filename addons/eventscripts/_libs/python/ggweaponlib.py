

dict_weaponInfo = {'deagle':        {'prop':'001', 'slot':2, 'ammo':7,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'ak47':          {'prop':'002', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle', '#sniper')},
                   'scout':         {'prop':'002', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle')},
                   'aug':           {'prop':'002', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle', '#sniper')},
                   'g3sg1':         {'prop':'002', 'slot':1, 'ammo':20,
                                     'tags':('#all', '#primary', '#rifle', '#sniper')},
                   'galil':         {'prop':'003', 'slot':1, 'ammo':35,
                                     'tags':('#all', '#primary', '#rifle')},
                   'famas':         {'prop':'003', 'slot':1, 'ammo':25,
                                     'tags':('#all', '#primary', '#rifle')},
                   'm4a1':          {'prop':'003', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle')},
                   'sg552':         {'prop':'003', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle')},
                   'sg550':         {'prop':'003', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#rifle', '#sniper')},
                   'm249':          {'prop':'004', 'slot':1, 'ammo':100,
                                     'tags':('#all', '#primary')},
                   'awp':           {'prop':'005', 'slot':1, 'ammo':10,
                                     'tags':('#all', '#primary', '#rifle', '#sniper')},
                   'tmp':           {'prop':'006', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#smg')},
                   'mp5navy':       {'prop':'006', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#smg')},
                   'glock':         {'prop':'006', 'slot':2, 'ammo':20,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'elite':         {'prop':'006', 'slot':2, 'ammo':30,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'm3':            {'prop':'007', 'slot':1, 'ammo':8,
                                     'tags':('#all', '#primary', '#shotgun')},
                   'xm1014':        {'prop':'007', 'slot':1, 'ammo':7,
                                     'tags':('#all', '#primary', '#shotgun')},
                   'mac10':         {'prop':'008', 'slot':1, 'ammo':30,
                                     'tags':('#all', '#primary', '#smg')},
                   'ump45':         {'prop':'008', 'slot':1, 'ammo':25,
                                     'tags':('#all', '#primary', '#smg')},
                   'usp':           {'prop':'008', 'slot':2, 'ammo':12,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'p228':          {'prop':'009', 'slot':2, 'ammo':13,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'fiveseven':     {'prop':'010', 'slot':2, 'ammo':20,
                                     'tags':('#all', '#secondary', '#pistol')},
                   'p90':           {'prop':'010', 'slot':1, 'ammo':50,
                                     'tags':('#all', '#primary', '#smg')},
                   'hegrenade':     {'prop':'011', 'slot':4, 'ammo':1,
                                     'tags':('#all', '#grenade')},
                   'flashbang':     {'prop':'012', 'slot':4, 'ammo':2,
                                     'tags':('#all', '#grenade')},
                   'smokegrenade':  {'prop':'013', 'slot':4, 'ammo':1,
                                     'tags':('#all', '#grenade')},
                   'knife':         {'prop':None,  'slot':3, 'ammo':None,
                                     'tags':('#all', '#knife')},
                   'c4':            {'prop':None,  'slot':5, 'ammo':None,
                                     'tags':('#all', '#objective')}}

class WeaponError(Exception):
    pass

class weaponInfo(object):
    def __init__(self, weapon):
        self.weapon = weapon
        
        if weapon not in dict_weaponInfo:
            raise WeaponError('Cannot get weapon (%s): not valid.' % weapon)
        
        self.attributes = dict_weaponInfo[weapon]
    
    def __coerce__(self, item):
        return (self.get('name'), item) if isinstance(item, str) else None
    
    def __getattr__(self, item):
        try:
            return self.get(item)
    
        except ValueError:
            raise AttributeError, 'Weapon instance has no attribute \'%s\'' % item
    
    def __getitem__(self, item):
        return self.get(item)
    
    def get(self, item):
        if item == 'prop':
            if self.attributes['prop']:
                return ('CBasePlayer.localdata.m_iAmmo.%s' % self.attributes['prop'])
            return None
        
        elif item in self.attributes:
            return self.attributes[item]
        
        raise ValueError('Unable to get attribute (%s): invalid attribute.' % item)

def getWeaponInfo(weapon):
    return weaponInfo(weapon)