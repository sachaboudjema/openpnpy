from flask import Flask, Response, request
from xml.etree import ElementTree
from copy import deepcopy


class PnpServer:

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
        self.app.run(*args, **kwargs)

    def handle_hello(self):
        '''What to do when a Pnp Agent calls in to the server.
        Returns an empty http 200 by default.
        '''
        return Response(status=200, headers={})

    def handle_work_request(self, work_request):
        '''What to do when a PnP agent sends a work request.
        The request passed as argument is of type PnpMessage.
        Should return a PnP message built using openpnpy.messages functions.
        Not implemented by default.
        '''
        raise NotImplementedError

    def handle_work_response(self, work_response):
        '''What to do when a PnP agent sends a work response.
        The response passed as argument is of type PnpMessage.
        Should return a PnP message built using openpnpy.messages functions.
        Not implemented by default.
        '''
        raise NotImplementedError
    

class PnpMessage:
    '''PnP XML message
    The plain ElementTree.Element can be accessed throught self.root.
    '''
    def __init__(self, element):
        self.root = element

    def __repr__(self):
        return '<PnpMessage {}>'.format(self.body.tag)

    @classmethod
    def from_string(cls, xmlstring):
        return cls(ElementTree.fromstring(xmlstring))

    def make_response(self, element):
        '''Builds a response to this message.
        Original message is copied and body is replaced by given element.This 
        allows to preserve session related attributes, such as udi and correlator.
        Element should be built using openpnpy.messages functions.
        '''
        response = deepcopy(self)
        response.body = element
        return response

    @property
    def udi(self):
        '''Unique Device Identifier. 
        A built in device id consisting of product id, version id, and the serial
        number. It is mandatory for all the messages that get exchanged between 
        the PnP agent and the PnP server.
        '''
        return self.root.get('udi')

    @property
    def username(self):
        '''Login username for the device.
        Applicable for all the messages that are sent from the PnP server to the 
        agent. The only exception is the initial exchange when there is no configuration 
        present on the new device.
        '''
        self.root.get('username')

    @username.setter
    def username(self, value):
        self.root.set('username', value)
    
    @property
    def password(self):
        self.root.get('password')

    @password.setter
    def password(self, value):
        '''Login password for the device.
        Applicable for all the messages that are sent from the PnP server to the 
        agent. The only exception is the initial exchange when there is no configuration 
        present on the new device.
        '''
        self.root.set('password', value)

    @property
    def body(self):
        '''Body of the PnP message.
        Can be one of info or request or response messages for various PnP services.
        '''
        return self.root[0]

    @body.setter
    def body(self, element):
        element.set('correlator', self.correlator)
        self.root[0] = element

    @property
    def correlator(self):
        '''A unique string to match requests and responses between agent and server.'''
        return self.body.get('correlator')

    @property
    def success(self):
        '''Success state of the last executed work request.
        None if the message is a work request.
        '''
        s = self.body.get('success')
        if s is not None:
            return bool(int(s))
        return s

    def to_string(self):
        return ElementTree.tostring(self.root)


class PnpResponse:

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, *args):
        agent_request = PnpMessage.from_string(request.get_data())
        server_response = agent_request.make_response(self.handler(agent_request))
        return server_response.to_string(), 200
