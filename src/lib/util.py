import os
from json import loads, dumps
from glob import glob
from random import randrange
import binascii
import sys
import hashlib
import yaml
from flatteneddict import FlattenedDict, stripslashes, flatten
import time
from  tempfile import NamedTemporaryFile
from math import sqrt
import json

gamedir = 'TESTDATA'

default_text="""#This is a python snippet
#It will be executed when the event occurs.
#You can use the following predefined objects to interact with the game
#item: The item that generated this event. item.lightradius += 1
#player: the player. player.put('core/combat/hitpoints', int(player.get('core/combat/hitpoints'))+1)
#target: the monster being targetted (only available for events that have a target). target.take_damage(4)
#messages: Send a message, warning or error. message.error('You have been cursed !!!')
#You can safely delete these comments if you want to, or just put your event handling code below.
#When you're done, save the file and close the text editor to return to Mirthless.
""".split('\n')

def realkey(key):
    key = stripslashes(key)
    if key.startswith('conditional'):
        conditions = [k for k in key.split('/') if '=' in k]
        for condition in conditions:
            newkey = key.split('/')
            newkey = newkey[newkey.index(condition):][1:]
            newkey = '/'.join(newkey)
            newkey = newkey.replace('.','/')
            key = newkey
    ret = []
    for k in key.split('/'):
        if k.startswith('__'):
            ret.append(k[3:])
        else:
            ret.append(k)
    return '/'.join(ret).strip('/')

def editsnippet(data):
    editor = os.getenv('EDITOR')
    if 'win' in sys.platform and not editor:
        editor = 'notepad.exe'
    elif not editor:
        if os.path.exists('/usr/bin/gedit'):
            editor = '/usr/bin/gedit'
        elif os.path.exists('/usr/bin/kate'):
            editor = '/usr/bin/kate'
    temp = NamedTemporaryFile(delete=False, suffix='.py')
    temp.write(data)
    temp.close()
    debug(editor, temp.name)
    os.system('%s %s' % (editor, temp.name))
    newtext = open(temp.name, 'r').read()
    os.unlink(temp.name)
    return newtext

def imagepath(s):
    parts=s.split(':')
    if len(parts) == 4:
        rot = parts[3]
    else:
        rot = 0
    return (parts[0], int(parts[1]), int(parts[2]), rot)

def forcegamedir():
    global gamedir
    if gamedir == 'TESTDATA':
        gamedir = os.path.dirname(os.path.abspath(__file__)) + '/..'
        gamedir = os.path.abspath(gamedir)
        return gamedir
    else:
     return gamedir



def file_list(directory, needle='*'):
    result = []
    global gamedir
    gamedir = forcegamedir()
    debug(gamedir)
    dirname = os.path.join(gamedir, directory)
    return glob(dirname+'/'+needle)

def file_path(directory, filename, new=False):
    global gamedir
    gamedir = forcegamedir()
    filename = os.path.join(gamedir, directory, filename)
    if new:
        return filename #Don't check for pre-existing when saving a new file
    if not os.path.exists(filename):
        testpath = os.path.join(gamedir,'testdata', directory, os.path.basename(filename))
        if os.path.exists(testpath):
            filename = testpath
        else:
            raise IOError(testpath)
    return filename

def filename_parser(displayname):
    name = displayname
    if not name.endswith('yaml'):
        name = '%s.yaml' % name
    return name.lower().replace(' ', '_').replace("'", "")


def debug(*args):
    out = '[DEBUG]:'
    for arg in args:
        out += ' ' + str(arg)
    sys.stderr.write('%s\n' % out)


def make_hash():
    """
    >>> hashes = []
    >>> for i in range(1,1000):
    ...     hashes.append(make_hash())
    ...
    >>> len(hashes) == len(list(set(hashes)))
    True
    """
    user_string = str(int(time.time())) + str(binascii.b2a_hex(os.urandom(64)))
    user_string = user_string.encode('utf-8')
    return str(hashlib.sha224(user_string).hexdigest())


def load_yaml(directory, filename):
    if not filename.endswith('.yaml'):
        filename = '%s.yaml' % filename
    filename = file_path(directory, filename)
    return FlattenedDict(yaml.load(open(filename).read()))

def dump_yaml(data):
    return yaml.safe_dump(data, default_flow_style=False, encoding='utf-8', width=1000)


def save_yaml(directory, filename, data, new=False):
    filename = file_path(directory, filename, new=new)
    strings = json.dumps(data, indent=4)
    open(filename,'w').write(strings)
    return filename

def price_in_copper(gold, silver, copper):
    s = gold * 10 + silver
    c = s * 10 + copper
    return c

def convert_money(copper):
    money = {"gold": 0, "silver": 0, "copper": copper}
    while money['copper'] > 10:
        money['silver'] += 1
        money['copper'] -= 10
    while money['silver'] > 10:
        money['gold'] += 1
        money['silver'] -= 10
    return money


def dice_list():
    return ['4', '6', '8', '10', '100', '12', '20']


def inrange(key1, key2):
    """
    >>> inrange(5,'6-7')
    False
    >>> inrange(5,'5')
    True
    >>> inrange(5,'4-7')
    True
    """
    if '-' in key2:
        minimum = int(key2.split('-')[0])
        maximum = int(key2.split('-')[1])
    else:
        minimum = int(key2)
        maximum = minimum
    if int(key1) >= minimum and int(key1) <= maximum:
        return True
    else:
        return False


def rolldice(numdice=1, numsides=20, modifier=0):
    """
    >>> x = rolldice(numdice=5, numsides=20, modifier=0)
    >>> x[0] >= 1
    True
    >>> x[0] <= 100
    True
    """
    total = 0
    numdice = int(numdice)
    numsides = int(numsides)
    modifier = int(modifier)
    for I in range(0, numdice):
            if numsides == 1:
                roll = randrange(0, numsides, 1)
            else:
                roll = randrange(1, numsides, 1)
            total = total + roll + modifier
    return (total, 'Rolled a %s-sided dice %s times with modifier %s: result %s' % (numsides, numdice, modifier, total))
