class AttrDict(dict):
    """`dict` subclass that also provides access to keys as attributes.

    Copied from
    https://github.com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py#L231.
    """

    def __getattr__(self, k):
        if k in self:
            return self[k]
        raise AttributeError(k)

    def __setattr__(self, k, v):
        (self.__setitem__, super().__setattr__)[k[0] == "_"](k, v)

    def __dir__(self):
        return dir(super()) + list(self.keys())
