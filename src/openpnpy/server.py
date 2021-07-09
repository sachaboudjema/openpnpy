"""This module provides a base server class to be derived and implemented 
according to the user's needs.
"""
from flask import Flask, Response, request
from xml.etree import ElementTree
from copy import deepcopy


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
            PnpResponse(self.handle_work_request),
            methods=['POST']
        )
        self.app.add_url_rule(
            '/pnp/WORK-RESPONSE', 'work_response',
            PnpResponse(self.handle_work_response),
            methods=['POST']
        )

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

        :param work_request: Work request sent by the PnP qgent
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

    def make_response(self, element):
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


class PnpResponse:
    """Decorator to create responses to the PnP request currently held by Flask's
    global request object.

    :param handler: function returning a PnP message body, as can be built using 
    the :py:mod:`openpnpy.messages` module
    :type handler: callable
    """
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, *args):
        """Gets the reponse message body by calling the handler function and 
        creates a proper PnP XML message with udi and correlaotr mathcing the PnP
        request.

        :return: HTTP response tuple composed of the PnP reponse message and 200
            status code
        :rtype: tuple
        """
        agent_request = PnpMessage.from_string(request.get_data())
        server_response = agent_request.make_response(self.handler(agent_request))
        return server_response.to_string(), 200
