import pytest
from xml.etree import ElementTree
from openpnpy.messages import bye, backoff


class TestBye:

    msg = bye()

    def test_return_type(self):
        assert isinstance(self.msg, ElementTree.Element)


class TestBackoff:

    msg = backoff(hours=1, minutes=23, seconds=11)

    def test_return_type(self):
        assert isinstance(self.msg, ElementTree.Element)
    
    def test_return_type(self):
        assert isinstance(self.msg, ElementTree.Element)
