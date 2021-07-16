"""This module provides a base server class to be derived and implemented 
according to the user's needs.
"""
import re
from flask import Flask, Response, request
from xml.etree import ElementTree
from copy import deepcopy

from openpnpy.messages import device_info


__all__ = ['PnpServer']


class PnpServer:
    """Wrapped Flask web server implementing PnP protocol endpoints.
    This class should be derived and the handler methods overloaded to implement
    behavior.
    See https://flask.palletsprojects.com/en/2.0.x/api/#application-object 
    for supported constructor params.
    """
    def __init__(self, *args, **kwargs):
        self.app = Flask(*args, **kwargs)
        self.app.add_url_rule('/pnp/HELLO', 'hello', self.handle_hello)
        self.app.add_url_rule(
            '/pnp/WORK-REQUEST', 'work_request',
            self.reply(self.handle_work_request),
            methods=['POST']
        )
        self.app.add_url_rule(
            '/pnp/WORK-RESPONSE', 'work_response',
            self.reply(self.handle_work_response),
            methods=['POST']
        )

    def reply(self, handler):
        """Decorator to create replies to the PnP request currently held in the
        global request object, using the body returned by the handler method."""
        def inner():
            agent_request = PnpMessage.from_string(request.get_data())
            server_response = agent_request.make_reply(handler(agent_request))
            return server_response.to_string(), 200
        return inner

    def run(self, *args, **kwargs):
        """Runs the Flask development server.
        See https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.run
        for supported params
        """
        self.app.run(*args, **kwargs)

    def handle_hello(self):
        """What to do when a PnP Agent calls in to the server.
        Should not be overridden in most cases.

        :return: HTTP response tuple as specified by Flask, defaults to empty http 
            200 by default.
        :rtype: tuple
        """
        return Response(status=200, headers={})

    def handle_work_request(self, work_request):
        """What to do when a PnP agent sends a work request.

        :param work_request: Work request sent by the PnP agent
        :type work_request: openpnpy.server.PnpMessage
        :return: Body element to be used in the repsonse message, as can be built 
            using the :py:mod:`openpnpy.messages` module
        :rtype: xml.etree.ElementTree.Element
        :raises NotImplementedError: To be implemented by user subclass
        """
        raise NotImplementedError

    def handle_work_response(self, work_response):
        """What to do when a PnP agent sends a work response.

        :param work_response: Work response sent by the PnP agent
        :type work_response: openpnpy.server.PnpMessage
        :return: Body element to be used in the repsonse message, as can be built 
            using the :py:mod:`openpnpy.messages` module
        :rtype: xml.etree.ElementTree.Element
        :raises NotImplementedError: To be implemented by user subclass
        """
        raise NotImplementedError


class PnpMessage:
    """PnP protocol XML message

    :param element: XML parsed message element 
    :type element: xml.etree.ElementTree.Element
    """
    def __init__(self, element):
        self.root = element

    def __repr__(self):
        return '<PnpMessage {} at {}>'.format(self.body.tag, id(self))

    @classmethod
    def from_string(cls, xmlstring):
        """Create an instance of PnpMessage from an XML string.
        """
        return cls(ElementTree.fromstring(xmlstring))

    def make_reply(self, element):
        """Builds a response to this message instance preserving session related 
        attributes.

        :param element: Response message body, as can be built using the 
            :py:mod:`openpnpy.messages` module
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
            the :py:mod:`openpnpy.messages` module
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

        :return: Success state, or None if the message is a work request
        :rtype: bool, None
        """
        s = self.body.get('success')
        if s is not None:
            return bool(int(s))
        return s

    def to_string(self):
        """Returns the message as na XML string.
        """
        return ElementTree.tostring(self.root)


def udi_to_dict(udi):
    '''Parse udi string to dict'''
    m = re.match(r'PID:(?P<PID>.+),VID:(?P<VID>.+),SN:(?P<SN>.+)', udi)
    return m.groupdict()


class PnpDeviceInfo(PnpMessage):

    def to_dict(self):
        info = udi_to_dict(self.udi)
        response = self.root.find('{*}response')
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