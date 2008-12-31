'''pickle.py - Pickle fixing automagic.

Courtesy of SuperDave at:
 * http://forums.mattie.info/cs/forums/viewtopic.php?p=226123#226123
 
To use the default pickle library use:
from pickle import pickle

or:

import realpickle as pickle'''

import es
import imp

gamedir = str(es.ServerVar('eventscripts_gamedir'))
pickle  = imp.load_module('realpickle', *imp.find_module('pickle', [gamedir + '/addons/eventscripts/_engines/python/Lib/']))

def hasColon():
    tempdir = gamedir.replace('\\', '/')
    tempdir = tempdir[tempdir.find('/') + 1:]
    return ':' in tempdir

if not hasColon():
    es.dbgmsg(1, 'Using cPickle')
    from cPickle import *

else:
    import struct
    from types import UnicodeType
    
    class FakeStr(str):
        def encode(self, enctype):
            # Get encoding type
            enctype = str(enctype).replace('-', '_')
            
            # Import the module
            i = __import__('encodings.%s' % enctype).__dict__[enctype]
            
            # Grab the codec
            if 'Codec' in i.__dict__:
                i = i.Codec
            
            return i.encode(self)
        
        def decode(self, enctype):
            # Get encoding type
            enctype = str(enctype).replace('-', '_')
            
            # Import the module
            i = __import__('encodings.%s' % enctype).__dict__[enctype]
            
            # Grab the codec
            if 'Codec' in i.__dict__:
                i = i.Codec
            
            return i.decode(self)
    
    def save_unicode(self, obj, pack=struct.pack):
        classicUnicode(self, FakeStr(obj), pack)
    
    classicUnicode = pickle.Pickler.dispatch[UnicodeType]
    pickle.Pickler.dispatch[UnicodeType] = save_unicode
    
    es.dbgmsg(1, 'Using FakePickler')
    from realpickle import *