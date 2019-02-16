import datetime, json
from bxml.builder import Builder
from bl.dict import Dict
from bl.string import String
from bsql.json_encoder import JSONEncoder


class Record(Dict):
    """A record from the database."""

    def __init__(self, db, **args):
        self.__dict__['db'] = db
        Dict.__init__(self, **args)

    def __repr__(self):
        """represent the object in a form that would enable it to be recreated"""
        sep = ', '
        return "%s(db, %s)" % (
            self.__class__.__name__,
            sep.join(["%s=%r" % (k, self.get(k)) for k in self.keys() if self.get(k) is not None]),
        )

    def __str__(self):
        sep = '\n\t'
        return "%s:%s%s" % (
            self.__class__.__name__,
            sep,
            sep.join(["%s: %s" % (k, self.get(k)) for k in self.keys() if self.get(k) is not None]),
        )

    def key_tuple(self, key=[]):
        """can be used as a dict key."""
        if key == []:
            key = self.keys()
        return tuple([self[k] for k in key])

    def dict(self, keys=None):
        return dict(**{k: self[k] for k in keys or self.keys()})

    def json(self, keys=None, indent=2, cls=None):
        return json.dumps(self.dict(keys=keys), indent=indent, cls=cls or JSONEncoder)

    def element(self, keys=None, namespace=None, minimize=True):
        B = Builder.single(namespace)
        return B(
            String(self.__class__.__name__).camelsplit().hyphenify().lower(),
            **{k: str(self.get(k)) for k in keys or self.keys() if self.get(k) or not minimize}
        )

    def using_keys(self, keys=[]):
        """return a copy of this record that only has the given keys. 
        Useful for generating a keyword-argument dictionary for select()
        """
        d = self.__class__(self.db)
        for k in keys:
            d[k] = self[k]
        return d

    def using_prefix(self, prefix, **args):
        """return an instance containing the args that have the given prefix, with prefix removed"""
        r = self.__class__.__init__(self, self.db)
        for k in [k for k in args.keys() if k[: len(prefix)] == prefix]:
            r[k[len(prefix) :]] = args[k]
        return r
