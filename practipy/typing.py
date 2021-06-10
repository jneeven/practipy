import typing


def _typeerr(arg, val, typ):
    return TypeError(f"{arg}=={val} not {typ}")


def type_hints(f):
    """Same as `typing.get_type_hints` but returns `{}` if not allowed type."""
    allowed_types = typing._allowed_types  # type:ignore
    return typing.get_type_hints(f) if isinstance(f, allowed_types) else {}


def annotations(o):
    """Annotations for `o`, or `type(o)`"""
    res = {}
    if not o:
        return res
    res = type_hints(o)
    if not res:
        res = type_hints(getattr(o, "__init__", None))
    if not res:
        res = type_hints(type(o))
    return res


def typed(func: typing.Callable):
    """Decorator to check param and return types at runtime. Copied from https://github.
    com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py
    .

    TODO: simplify this! And use zookeeper type code instead.
    """
    names = func.__code__.co_varnames
    anno = annotations(func)
    ret = anno.pop("return", None)

    def _f(*args, **kwargs):
        kw = {**kwargs}
        if len(anno) > 0:
            for i, arg in enumerate(args):
                kw[names[i]] = arg
            for k, v in kw.items():
                if k in anno and not isinstance(v, anno[k]):
                    raise _typeerr(k, v, anno[k])
        res = func(*args, **kwargs)
        if ret is not None and not isinstance(res, ret):
            raise _typeerr("return", res, ret)
        return res
