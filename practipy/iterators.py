import itertools
from typing import Callable, Iterable


def batch(iterable: Iterable, chunksize: int, output_type: Callable = list):
    """Iterates over iterable in chunks.`output_type` can be a class or a function, and
    will be called to convert the islice object of the current batch to the desired
    output format."""
    iterable = iter(iterable)
    while True:
        chunk = output_type(itertools.islice(iterable, chunksize))
        if not chunk or len(chunk) == 0:
            return
        yield chunk
