from typing import Sequence


class Dict(dict):
    """Improved dictionary class that:

    - Provides access to keys as attributes.
    - Has some of the same operators as sets, e.g. can be intersected with another one.

    Attribute part copied from
    https://github.com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py#L231.
    """

    # TODO: add other set methods like union, diff etc.
    def intersect(self, *other: "Dict") -> "Dict":
        """Intersect this dictionary with the other ones based on their keys."""
        shared_keys = self.keys()
        for d in other:
            shared_keys &= d.keys()

        return self.__class__({k: self[k] for k in shared_keys})

    @classmethod
    def intersect_all(cls, dicts: Sequence["Dict"]) -> "Dict":
        """Intersect a sequence of dictionaries based on their keys."""
        return dicts[0].intersect(*dicts[1:])

    def __getattr__(self, k):
        if k in self:
            return self[k]
        raise AttributeError(k)

    def __setattr__(self, k, v):
        (self.__setitem__, super().__setattr__)[k[0] == "_"](k, v)

    def __dir__(self):
        return dir(super()) + list(self.keys())
