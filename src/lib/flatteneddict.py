import yaml
import sys

def flatten(init, lkey=''):
    ret = {}
    for rkey, val in list(init.items()):
        key = lkey + rkey
        if isinstance(val, dict) and val:
            ret.update(flatten(val, key + '/'))
        else:
            ret[key] = val
    return ret


def stripslashes(s):
    while s.startswith('/'):
        s = s[1:]
    while s.endswith('/'):
        s = s[1:]
    return s

def debug(*args):
    out = '[DEBUG]:'
    for arg in args:
        out += ' ' + str(arg)
    sys.stderr.write('%s\n' % out)

class FlattenedDict(dict):
    # def __init__(self, data={}):
    #     if isinstance(data, str):
    #         data = yaml.load(data)
    #     self.data = data

    def readall(self, key):
        """
        >>> FlattenedDict({'a/b': 1, 'f/g':2, 'a/b/c' :2 }).readall('/a') == {'a/b': 1, 'a/b/c':2} 
        True
        """
        result = {}
        key = stripslashes(key)
        for k in self:
            if k.startswith(key):
                result[k] = self[k]
        return result

    def __str__(self):
        return yaml.safe_dump(dict(self), default_flow_style=False, encoding='utf-8')

    # def __getitem__(self, key ):      
    #     return self.getvalue(key)

    # def __iter__(self):
    #     for k in self.data:
    #         yield k
    # def __len__(self):
    #     return len(self.data)

    # def __setitem__(self, key, value):
    #     self.data[stripslashes(key)] = value

    # def __delitem__(self, key):
    #     del self.objdata[stripslashes(key)]

    # def __call__(self):
    #     return self.data

    # def keys(self):
    #     return self.data.keys


    def readsubtree(self, key):
        """
        >>> FlattenedDict({'a/b': 1, 'f/g':2, 'a/c/x' :2 }).readsubtree ('/a') == {'b': 1, 'c/x': 2}
        True
        """
        result = {}
        key = stripslashes(key)
        splitkey = key.split('/')
        parent = splitkey[-1]
        parentsize = len(splitkey) -1
        for k in self:
            if k.startswith(key):
                keys = k.split('/')
                if not keys[-1] == parent:
                    subkey = '/'.join(keys[keys.index(parent)+1:])
                    result[subkey] = self[k]
        return result

    def getsubtree(self, key):
        return self.readsubtree(key)

    def writekey(self, key, value):
        key = stripslashes(key)
        self[key] = value

    def writesubtree(self, key, data):
        self.deltree(key)
        key = stripslashes(key)
        d = flatten(data)
        for k in d:
            subkey = key+'/'+k
            self[subkey] = d[k]
        return self

    def deltree(self, key):
        key = stripslashes(key)
        delme = []
        for k in self:
            if k.startswith(key):
                delme.append(k)
        for k in delme:
            del self[k]
        self[key] = ''
        return self

    def subkeys(self, key=None, dictionary=None):
        """
        >>> #Return a list of keys directly beneath the current one in the hierarchy
        >>> sorted(FlattenedDict({'a/b': 1, 'f/g':2, 'a/c/x' :2 }).subkeys('a')) == ['b', 'c']
        True
        >>> FlattenedDict({'a/b': 1, 'f/g':2, 'a/c/x' :2 }).subkeys() == ['a', 'f']
        True
        """
        if dictionary is None:
            dictionary = self
        result = []
        for k in dictionary:
            keys = k.split('/')
            if key and key in keys:
                keys = keys[keys.index(key)+1:]
                result.append(keys[0])
            elif key:
                continue
            else:
                result.append(keys[0])
        return list(set(result))


