import re

# TODO: lazily compile these.
_c2w_re = re.compile(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))")
_camel_re1 = re.compile("(.)([A-Z][a-z]+)")
_camel_re2 = re.compile("([a-z0-9])([A-Z])")


def camel2words(string: str):
    """Convert CamelCase to 'spaced words' Copied from https://github.com/fastai/fastcor
    e/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py."""
    return re.sub(_c2w_re, r" \1", string)


def camel2snake(string: str):
    """Convert CamelCase to snake_case.

    Copied from
    https://github.com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py
    """
    s1 = re.sub(_camel_re1, r"\1_\2", string)
    return re.sub(_camel_re2, r"\1_\2", s1).lower()


def remove_prefix(string: str, prefix: str):
    # Removes the specified prefix from the string, if present.
    if string.startswith(prefix):
        string = string[len(prefix) :]
    return string


def snake2camel(string: str):
    """Convert snake_case to CamelCase.

    Copied from
    https://github.com/fastai/fastcore/blob/0df9c4a8e9a1756fe26fccffab8976195563c8a9/fastcore/basics.py
    """
    return "".join(string.title().split("_"))
