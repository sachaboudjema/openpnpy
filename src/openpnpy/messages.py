import re
from xml.etree import ElementTree
from copy import deepcopy


__all__ = ['PnpMessage']


class PnpMessage:
    """PnP protocol XML message

    :param element: XML parsed message element 
    :type element: xml.etree.ElementTree.Element
    """
    def __init__(self, element):
        self.root = element

    def __repr__(self):
        return '<PnpMessage {} at {}>'.format(self.body.tag, id(self))

    def __str__(self):
        return f"{self.correlator} {self.udi} {self.body.tag} success={self.success}"

    @classmethod
    def from_string(cls, xmlstring):
        """Create an instance of PnpMessage from an XML string.
        """
        return cls(ElementTree.fromstring(xmlstring))

    def make_reply(self, element):
        """Builds a response to this message instance preserving session related 
        attributes.

        :param element: Response message body, as can be built using the 
            :py:mod:`openpnpy.services` module
        :type element: xml.etree.ElementTree.Element
        :return: New PnP message with given body
        :rtype: openpnpy.server.PnpMessage
        """
        response = deepcopy(self)
        response.body = element
        return response

    @property
    def udi(self):
        """Unique Device Identifier. 
        A built in device id consisting of product id, version id, and the serial
        number. It is mandatory for all the messages that get exchanged between 
        the PnP agent and the PnP server.
        """
        return self.root.get('udi')

    @property
    def username(self):
        """Login username for the device.
        Applicable for all the messages that are sent from the PnP server to the 
        agent. The only exception is the initial exchange when there is no configuration 
        present on the new device.
        """
        self.root.get('username')

    @username.setter
    def username(self, value):
        self.root.set('username', value)
    
    @property
    def password(self):
        """Login password for the device.
        Applicable for all the messages that are sent from the PnP server to the 
        agent. The only exception is the initial exchange when there is no configuration 
        present on the new device.
        """
        self.root.get('password')

    @password.setter
    def password(self, value):
        self.root.set('password', value)

    @property
    def body(self):
        """Body of the PnP message.
        Can be one of info or request or response messages for various PnP services.
        """
        return self.root[0]

    @body.setter
    def body(self, element):
        """Replaces the message body.
        The message correlator is apended to the provided body element.

        :param element: Body element to be replaced with, as can be built using 
            the :py:mod:`openpnpy.services` module
        :type element: xml.etree.ElementTree.Element
        """
        element.set('correlator', self.correlator)
        self.root[0] = element

    @property
    def correlator(self):
        """A unique string to match requests and responses between agent and server.
        """
        return self.body.get('correlator')

    @property
    def success(self):
        """Success state of the last executed work request.

        :return: Success state, None if the message is not a work response
        :rtype: bool, None
        """
        s = self.body.get('success')
        if s is not None:
            return bool(int(s))
        return s

    def to_string(self):
        """Returns the message as an XML string.
        """
        return ElementTree.tostring(self.root)


def udi_to_dict(udi):
    """Parses a UDI string to an equivalent dictionnary

    :param udi: UDI string as found in a PnP message header element
    :type udi: str
    :return: UDI dict
    :rtype: dict
    """
    m = re.match(r'PID:(?P<PID>.+),VID:(?P<VID>.+),SN:(?P<SN>.+)', udi)
    return m.groupdict()


def device_info_dict(device_info):
    """Parses an XML Device Info reponse to an equivalent dictionnary

    :param device_info: Agent response message to a device_info service request
    :type device_info: PnpMessage
    :return: Dictionnary of the device info
    :rtype: dict
    """
    info = udi_to_dict(device_info.udi)
    response = device_info.root.find('{*}response')
    udi = response.find('{*}udi')
    image_info = response.find('{*}imageInfo')
    hw_info = response.find('{*}hardwareInfo')
    profile_info = response.find('{*}profileInfo')
    file_systems =  response.find('{*}fileSystemList')
    if file_systems:
        info['fileSystemList'] = list()
        for fs in file_systems:
            info['fileSystemList'].append({
                'name': fs.get('name'),
                'type': fs.get('type'),
                'writable': fs.get('writable'),
                'readable': fs.get('readable'),
                'size': fs.get('size'),
                'freespace': fs.get('freespace'),
            })
    if udi:
        info['primary-chassis'] = udi_to_dict(udi.find('{*}primary-chassis').text)  
        ha = udi.find('{*}ha-device')
        stack = udi.find('{*}stacked-switch')
        if stack:
            info['stacked-switch'] = list()
            for member in stack:
                info['stacked-switch'].append({
                    'slot': member.get('slot'),
                    **udi_to_dict(member.text)
                })
        if ha:
            info['ha-device'] = list()
            for standby in ha:
                info['ha-device'].append(udi_to_dict(standby.text))
    if hw_info:
        info['hostname'] = hw_info.find('{*}hostname').text
        info['vendor'] = hw_info.find('{*}vendor').text
        info['platformName'] = hw_info.find('{*}platformName').text
        info['processorType'] = hw_info.find('{*}processorType').text
        info['hwRevision'] = hw_info.find('{*}hwRevision').text
        info['mainMemSize'] = hw_info.find('{*}mainMemSize').text
        info['ioMemSize'] = hw_info.find('{*}ioMemSize').text
        info['boardId'] = hw_info.find('{*}boardId').text
        info['boardReworkId'] = hw_info.find('{*}boardReworkId').text
        info['processorRev'] = hw_info.find('{*}processorRev').text
        info['midplaneVersion'] = hw_info.find('{*}midplaneVersion').text
        info['location'] = hw_info.find('{*}location').text
    if image_info:
        info['versionString'] = image_info.find('{*}versionString').text
        info['imageFile'] = image_info.find('{*}imageFile').text
        info['imageHash'] = image_info.find('{*}imageHash').text
        info['returnToRomReason'] = image_info.find('{*}returnToRomReason').text
        info['bootVariable'] = image_info.find('{*}bootVariable').text
        info['bootLdrVariable'] = image_info.find('{*}bootLdrVariable').text
        info['configVariable'] = image_info.find('{*}configVariable').text
        info['configReg'] = image_info.find('{*}configReg').text
        info['configRegNext'] = image_info.find('{*}configRegNext').text
    if profile_info:
        info['profileInfo'] = list()
        for profile in profile_info:
            primary_server = profile.find('{*}primary-server') 
            backup_server = profile.find('{*}backup-server')
            p = {
                'profile-name': profile.get('profile-name'),
                'discovery-created': profile.get('discovery-created'),
                'created-by': profile.get('created-by'),
            }
            ps = {
                'protocol': primary_server.find('{*}protocol').text,
            }
            for e in primary_server.find('{*}server-address').iter():
                if 'port' in e.tag:
                    ps.update({'port': e.text})
                else:
                    ps.update({'server-address': e.text})
                    ps.update({'server-address-type': e.tag})
            p.update({'primary-server': ps})
            if backup_server:
                bs = {
                    'protocol': backup_server.find('{*}protocol').text,
                }
                for e in backup_server.find('{*}server-address').iter():
                    if 'port' in e.tag:
                        bs.update({'port': e.text})
                    else:
                        bs.update({'server-address': e.text})
                p.update({'backup-server': bs})
            info['profileInfo'].append(p)
    return info