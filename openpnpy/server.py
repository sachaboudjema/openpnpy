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
        '''Defines what to do when a Pnp Agent calls in to the server.
        Returns an empty http 200 by default.
        '''
        return Response(status=200, headers={})

    def handle_work_request(self, work_request):
        '''Defines what to do when a PnP agent sends a work request.
        The request passed as argument is of type PnpMessage.
        Should return a PnP message built using openpnpy.messages functions.
        Not implemented by default.
        '''
        raise NotImplementedError

    def handle_work_response(self, work_response):
        '''Defines what to do when a PnP agent sends a work response.
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
        '''Builds a new PnpMessage from this one, replacing the body with given element.
        The element shoudl be built using openpnpy.messages functions.
        This allowes to preserve session related atrtibuts, such as udi and correlator.
        '''
        response = deepcopy(self)
        response.body = element
        return response

    @property
    def udi(self):
        return self.root.get('udi')

    @property
    def username(self):
        self.root.get('username')

    @username.setter
    def username(self, value):
        self.root.set('username', value)
    
    @property
    def password(self):
        self.root.get('password')

    @password.setter
    def password(self, value):
        self.root.set('password', value)

    @property
    def body(self):
        return self.root[0]

    @body.setter
    def body(self, element):
        element.set('correlator', self.correlator)
        self.root[0] = element

    @property
    def correlator(self):
        return self.body.get('correlator')

    def to_string(self):
        return ElementTree.tostring(self.root)


class PnpResponse:

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, *args):
        agent_request = PnpMessage.from_string(request.get_data())
        server_response = agent_request.make_response(self.handler(agent_request))
        return server_response.to_string(), 200
