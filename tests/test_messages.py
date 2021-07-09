from xml.etree import ElementTree
from openpnpy.messages import bye, backoff


class TestBye:

    def test_return_type(self):
        assert isinstance(bye(), ElementTree.Element)


class TestBackoff:

    def test_return_type(self):
        assert isinstance(backoff(), ElementTree.Element)
