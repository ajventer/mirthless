import os
from json import loads, dumps
from glob import glob
from random import randrange
import binascii
import sys
import hashlib
import yaml

gamedir = 'TESTDATA'

def forcegamedir():
    """
    >>> forcegamedir().endswith('mirthless')
    True
    """
    global gamedir
    if gamedir == 'TESTDATA':
        gamedir = os.path.abspath(__file__) + '/../../'
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

def file_path(directory, filename):
    global gamedir
    gamedir = forcegamedir()
    debug(gamedir)
    filename = os.path.join(gamedir, directory, filename)
    if not os.path.exists(filename):
        testpath = os.path.join(gamedir,'testdata', directory, os.path.basename(filename))
        if os.path.exists(testpath):
            filename = testpath
        else:
            raise IOError(testpath)
    debug ('Loading file: ', filename)
    return filename

def user_hash():
    user_string = '%s%s' % (bottle.request.environ.get('REMOTE_ADDR'), bottle.request.environ.get('HTTP_USER_AGENT'))
    user_string = user_string.encode('utf-8')
    return hashlib.sha224(user_string).hexdigest()


def filename_parser(displayname):
    name = displayname
    if not name.endswith('json'):
        name = '%s.json' % name
    return name.lower().replace(' ', '_').replace("'", "")


def debug(*args):
    out = '[DEBUG]:'
    for arg in args:
        out += ' ' + str(arg)
    sys.stderr.write('%s\n' % out)


def npc_hash():
    """
    >>> hashes = []
    >>> for i in range(1,1000):
    ...     hashes.append(npc_hash())
    ...
    >>> len(hashes) == len(list(set(hashes)))
    True
    """
    return str(binascii.b2a_hex(os.urandom(64)))


def realkey(key):
    ret = []
    for k in key.split('/'):
        if k.startswith('__'):
            ret.append(k[3:])
        else:
            ret.append(k)
    return '/'.join(ret).strip('/')

def stripslashes(s):
    while s.startswith('/'):
        s = s[1:]
    while s.endswith('/'):
        s = s[1:]
    return s


def readkey(key, json, default=None):
    key = stripslashes(key)
    debug('Reading ', key)
    if key in json:
        return json[key]
    else:
        return default

def readall(key, json):
    """
    >>> readall ('/a', {'a/b': 1, 'f/g':2, 'a/b/c' :2 }) == {'a/b': 1, 'a/b/c':2} 
    True
    """
    result = {}
    key = stripslashes(key)
    for k in json:
        if k.startswith(key):
            result[k] = json[k]
    return result

def readsubtree(key, json):
    """
    >>> readsubtree ('/a', {'a/b': 1, 'f/g':2, 'a/c/x' :2 }) == {'b': 1, 'c/x': 2}
    True
    """
    result = {}
    key = stripslashes(key)
    splitkey = key.split('/')
    parent = splitkey[-1]
    parentsize = len(splitkey) -1
    for k in json:
        if k.startswith(key):
            keys = k.split('/')
            if not keys[-1] == parent:
                subkey = '/'.join(keys[keys.index(parent)+1:])
                result[subkey] = json[k]
    return result

def subkeys(json):
    result = []
    for k in json:
        keys = k.split('/')
        result.append(keys[0])
    return list(set(result))


def writekey(key, value, json):
    key = stripslashes(key)
    json[key] = value

def flatten(init, lkey=''):
    ret = {}
    for rkey, val in list(init.items()):
        key = lkey + rkey
        if isinstance(val, dict) and val:
            ret.update(flatten(val, key + '/'))
        else:
            ret[key] = val
    return ret

def writesubtree(json, key, data):
    emptytree(json,key)
    key = stripslashes(key)
    d = flatten(data)
    for k in d:
        subkey = key+'/'+k
        json[subkey] = d[k]
    return json

def emptytree(json, key):
    key = stripslashes(key)
    delme = []
    for k in json:
        if k.startswith(key):
            delme.append(k)
    for k in delme:
        del json[k]
    json[key] = ''
    return json


def readyaml(directory, filename):
    path = file_path(directory, filename)
    debug('Loading %s ' % (path))
    return yaml.load(open(path).read())


def load_json(directory, filename):
    filename = file_path(directory, filename)
    return yaml.load(open(filename).read())

def save_json(directory, filename, json):
    filename = file_path(directory, filename)
    strings = yaml.safe_dump(json, default_flow_style=False, encoding='utf-8').split('\n')
    strings.sort()
    strings = '\n'.join(strings)
    open(filename,'w').write(strings)

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
