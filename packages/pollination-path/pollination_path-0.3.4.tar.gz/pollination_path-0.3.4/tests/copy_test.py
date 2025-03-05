from pollination.path.copy import Copy, CopyMultiple
from queenbee.plugin.function import Function


def test_copy():
    function = Copy().queenbee
    assert function.name == 'copy'
    assert isinstance(function, Function)


def test_copy_multiple():
    function = CopyMultiple().queenbee
    assert function.name == 'copy-multiple'
    assert isinstance(function, Function)
