import pytest

from practipy.testing import MockMeta


class BaseClass:
    SOME_CLASS_VARIABLE = [1, 2, 3]
    ANOTHER_VARIABLE = 0

    def __init__(self):
        self.x = 1

    def function_a(self, *args):
        pass

    def function_b(self, *args):
        return "Base value"

    @property
    def property_a(self):
        return 5


class MockedClass(BaseClass, metaclass=MockMeta):
    ANOTHER_VARIABLE = 100

    def __init__(self):
        super().__init__()

    def function_b(self, *args):
        return "Mocked value"

    def function_c(self, *args):
        return True

    @property
    def property_a(self):
        return 3


def test_own_attributes():
    assert MockedClass.__own_attributes__ == {
        # These are explicitly defined
        "ANOTHER_VARIABLE",
        "__init__",
        "function_b",
        "function_c",
        "property_a",
        # These are apparently always "overridden", for any new class.
        "__module__",
        "__qualname__",
        "__classcell__",
    }


def test_overridden_attributes():
    # These should be accessible and return the right values.
    assert MockedClass.ANOTHER_VARIABLE == 100

    instance = MockedClass()
    assert instance.ANOTHER_VARIABLE == 100  # Should be accessible from instance too
    assert instance.x == 1
    assert instance.function_b() == "Mocked value"
    assert instance.function_c() == True
    assert instance.property_a == 3


def test_protected_attributes():
    with pytest.raises(NotImplementedError):
        MockedClass.SOME_CLASS_VARIABLE

    instance = MockedClass()

    with pytest.raises(NotImplementedError):
        instance.SOME_CLASS_VARIABLE

    with pytest.raises(NotImplementedError):
        instance.function_a()
