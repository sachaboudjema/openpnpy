import re
from copy import deepcopy
from xml.etree import ElementTree
from contextlib import contextmanager


__all__ = ['backoff', 'device_info']


class ContextualTreeBuilder(ElementTree.TreeBuilder):
    '''Convinience class to allow using contexts with TreeBuilder'''
    @contextmanager
    def start(self, tag, attrib={}):
        try:
            yield super().start(tag, attrib)
        finally:
            super().end(tag)


def backoff(seconds=0, reason='No Reason'):
    '''Inform the PnP agent to connect back after some time.'''
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:backoff}request'):
        with ctb.start('backoff'):
            with ctb.start('reason'):
                ctb.data(reason)
            with ctb.start('callBackAfter'):
                with ctb.start('seconds'):
                    ctb.data(str(seconds))
    return ctb.close()


def device_info(type='all'):
    '''Request to retrieve device information from PnP agent.
    Type can take the following values: image, hardware, filesystem, udi,
    profile, all
    '''
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:device-info}request'):
        with ctb.start('deviceInfo', {'type': type}):
            pass
    return ctb.close()

