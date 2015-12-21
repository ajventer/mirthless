from util import debug, dump_yaml, make_hash, gamedir, save_yaml
from flatteneddict import FlattenedDict, stripslashes

def event(obj, key, localvars):
    code = '\n'.join(obj.get(key, ''))
    debug('Got code %s' % code)
    #localvars['campaign'] = campaign()
    if code:
        try:
            exec (code, {}, localvars)
        except Exception as e:
            raise Exception("Exception [%s], while running event code, key: %s, object: %s, localvars: %s\n%s" % (e, key, obj.displayname(), localvars, code))


class EzdmObject(object):
    objdata = FlattenedDict()

    def __init__(self, objdata):
        self.objdata = objdata
        self.objdata = FlattenedDict(self.objdata)
        if not self.get_hash():
            self.set_hash()

    @property
    def animations(self):
        return self.getsubtree('animations')

    def set_hash(self):
        """
        >>> o = EzdmObject({'test': 0})
        >>> hash = o.set_hash()
        >>> hash == o.get_hash()
        True
        """
        myhash = make_hash()
        self.put('hash', myhash)
        return myhash

    def get_hash(self):
        return self.get('hash', '')

    def __call__(self):
        """
        >>> o = EzdmObject({'test': 0})
        >>> o()['test'] == 0
        True
        """
        return self.objdata

    def __str__(self):
        return dump_yaml(dict(self()))

    def update(self, objdata):
        """
        >>> j1 = {'test': 0}
        >>> j2 = {'foo': 'bar'}
        >>> o = EzdmObject(j1)
        >>> o.update(j2)
        >>> o()['foo'] == 'bar'
        True

        """
        self.__init__(objdata)

    def get(self, key, default=None):
        """
        >>> o = EzdmObject({'a/b': 1, 'a/c': 2})
        >>> o.get('/a', '') 
        ''
        >>> o.get('/a/b', '')
        1
        >>> o.get('/f/g', 5)
        5
        """
        key = stripslashes(key)
        if not self() or not key in self():
            if default is not None:
                return default
        return self()[key]

    def getall(self, key):
        return readall(key,self())

    def getsubtree(self, key):
        return self.objdata.readsubtree(key)

    def put(self, key, value):
        """
        >>> o = EzdmObject({'a/b': 1, 'a/c': 2})
        >>> o.put('/f/g', 16)
        >>> o()['f/g']
        16
        """
        self.objdata[stripslashes(key)] = value

    def putsubtree(self, key, value):
        return self.objdata.writesubtree(key, value)

    def filename(self):
        return '%s.yaml' % self.get_hash()

    def save_to_file(self, directory):
        filename = save_yaml(directory, self.filename(), dict(self()), new=True)
        return filename

    def save(self):
        #TODO - save to player save slot
        pass
        
