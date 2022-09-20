import functools
import inspect
from types import new_class


class _NotImplementedDescriptor:
    """Used to prevent access to unmocked attributes on a MockMeta class."""

    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is not None:
            owner = instance.__class__

        raise NotImplementedError(
            f"{self.name} has not been explicitly mocked on {owner.__name__}! "
            "If you need it, implement it yourself."
        )


@functools.lru_cache(maxsize=1)
def _get_default_attributes() -> set:
    """Returns the attributes that are defined on any class."""
    return set(dir(new_class("Stub")))


class MockMeta(type):
    """Metaclass for mock classes.

    This is useful to make your mock class subclass its target (such that e.g.
    isinstance will work as expected). It will raise an error on any method that isn't
    defined on the mock class, so you can be sure that you're not accidentally doing
    unexpected things in your tests.

    Example usage:
    ```python
        class MockedTargetClass(TargetClass, metaclass=MockMeta):
            def some_overridden_method(self):
                print("This is the only function that can be called on this instance!")
    ```
    """

    def __new__(cls, name, bases, dict_):
        # dict_ is a dictionary of all the things defined on this new subclass, e.g. a
        # custom init, any overridden functions etc.
        # First, just create the class like we normally would.
        subclass = super().__new__(cls, name, bases, dict_)

        # Then store all the keys that are defined on this subclass for future use.
        subclass.__own_attributes__ = set(dict_.keys())

        # Obtain all attributes of all parent classes that do not also have the MockMeta
        # metaclass.
        parent_attrs = set()
        for c in inspect.getmro(subclass)[1:]:
            if not issubclass(type(c), MockMeta):
                parent_attrs |= set(dir(c))

        # Anything that was defined (or overridden) on the subclass itself should be
        # ignored here.
        parent_attrs -= subclass.__own_attributes__
        # Any attribute shared by ALL classes (e.g. __class__) should not be
        # overwritten either.
        parent_attrs -= _get_default_attributes()

        # All the remaining (i.e. inherited) attributes are made inaccessible.
        for attr_name in parent_attrs:
            setattr(subclass, attr_name, _NotImplementedDescriptor(name=attr_name))

        return subclass
