from xml.etree import ElementTree
from contextlib import contextmanager


__all__ = ['backoff', 'device_info']


class ContextualTreeBuilder(ElementTree.TreeBuilder):
    """Convinience class to allow using contexts with TreeBuilder.
    """
    @contextmanager
    def start(self, tag, attrib={}):
        try:
            yield super().start(tag, attrib)
        finally:
            super().end(tag)


def backoff(seconds=0, reason='No Reason'):
    """Inform the PnP agent to connect back after some time.

    :param seconds: Seconds to wait before connecting back, defaults to 0
    :type seconds: int, optional
    :param reason: Reason of the backoff request, defaults to 'No Reason'
    :type reason: str, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
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
    """Request to retrieve device information from PnP agent.
    Type can take the following values: .

    :param type: Info sections to be sent, can be 'image', 'hardware', 'filesystem', 
        'udi', 'profile' or 'all', defaults to 'all'
    :type type: str, optional
    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:device-info}request'):
        with ctb.start('deviceInfo', {'type': type}):
            pass
    return ctb.close()


def bye():
    """Acknowledge the receipt of PnP response and signal the end of the transaction.
    This is applicable only when the transport protocol is HTTP and HTTPS.

    :return: XML element to be used as a PnP message body
    :rtype: xml.etree.ElementTree.Element
    """
    ctb = ContextualTreeBuilder()
    with ctb.start('{urn:cisco:pnp:work-info}info'):
        with ctb.start('workInfo'):
            with ctb.start('bye'):
                pass
    return ctb.close()