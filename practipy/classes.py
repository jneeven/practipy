from typing import Sequence


class Dict(dict):
    """Improved dictionary class that:

    - Provides access to keys as attributes.
    - Has some of the same operators as sets, e.g. can be intersected with another one.

    Attribute part copied from
    https://github.com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py#L231.

    TO DO @jneeven: Add unit tests.
    """

    def difference(self, *others: "Dict") -> "Dict":
        """Return a new dict with keys in this dict that are not in the others."""
        diff_keys = self.keys()
        for d in others:
            diff_keys -= d.keys()

        return self.__class__({k: self[k] for k in diff_keys})

    def intersection(self, *others: "Dict") -> "Dict":
        """Return a new dict with keys common to this dict and all others."""
        shared_keys = self.keys()
        for d in others:
            shared_keys &= d.keys()

        return self.__class__({k: self[k] for k in shared_keys})

    def symmetric_difference(self, *others: "Dict") -> "Dict":
        """Return a new dict with keys from either this dict or the others but not
        both."""

        others_union = self.__class__.union_of(others)
        keys_unique_to_self = self.keys() - others_union.keys()
        keys_unique_to_others = others_union.keys() - self.keys()

        return self.__class__(
            {
                **{k: self[k] for k in keys_unique_to_self},
                **{k: others_union[k] for k in keys_unique_to_others},
            }
        )

    def union(self, *others: "Dict") -> "Dict":
        """Return a new dict with keys from this dict and all others."""
        output = self.__class__(self)
        for d in others:
            output.update(d)

        return output

    @classmethod
    def intersection_of(cls, dicts: Sequence["Dict"]) -> "Dict":
        """Intersect a sequence of dictionaries based on their keys."""
        return dicts[0].intersection(*dicts[1:])

    @classmethod
    def union_of(cls, dicts: Sequence["Dict"]) -> "Dict":
        """Return a new dict that is the union of all others."""
        return dicts[0].union(*dicts[1:])

    def __getattr__(self, k):
        if k in self:
            return self[k]
        raise AttributeError(k)

    def __setattr__(self, k, v):
        (self.__setitem__, super().__setattr__)[k[0] == "_"](k, v)

    def __dir__(self):
        return dir(super()) + list(self.keys())
