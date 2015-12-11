from util import readkey, writekey, debug
from json import dumps
from frontend import mode


def event(obj, key, localvars):
    code = obj.get(key, '')
    debug('Got code %s' % code)
    #localvars['campaign'] = campaign()
    if code:
        try:
            exec (code, {}, localvars)
        except Exception as e:
            raise Exception("Exception %s, while running event code, key: %s, object: %s, localvars: %s\n%s" % (e, key, obj.displayname(), localvars, code))


class EzdmObject(object):
    json = {}

    def __init__(self, json):
        self.json = json

    def __call__(self):
        """
        >>> o = EzdmObject({'test': 0})
        >>> o() == {'test': 0}
        True
        """
        return self.json

    def __str__(self):
        """
        >>> o = EzdmObject({'test': 0})
        >>> str(o) == dumps({'test': 0}, indent=4)
        True
        """
        return dumps(self(), indent=4)

    def update(self, json):
        """
        >>> j1 = {'test': 0}
        >>> j2 = {'foo': 'bar'}
        >>> o = EzdmObject(j1)
        >>> o.update(j2)
        >>> o() == j2
        True

        """
        self.__init__(json)

    def get(self, key, default):
        """
        >>> o = EzdmObject({'a': {'b': 1, 'c': 2}})
        >>> o.get('/a', '') == {'b': 1, 'c': 2}
        True
        >>> o.get('/a/b', '')
        1
        >>> o.get('/f/g', 5)
        5
        """
        if not self():
            return default
        return readkey(key, self(), default)

    def put(self, key, value):
        """
        >>> o = EzdmObject({'a': {'b': 1, 'c': 2}})
        >>> o.put('/f/g', 16)
        >>> o()['f']['g']
        16
        """
        return writekey(key, value, self.json)

    def save(self):
        pass
