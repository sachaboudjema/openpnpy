"""This module provides a base server class to be derived and implemented 
according to the user's needs.
"""
from flask import Flask, Response, request
from openpnpy.messages import PnpMessage


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
            self.app.logger.info('AGENT REQUEST: %s', agent_request)
            self.app.logger.debug('%s', agent_request.to_string())
            self.app.logger.info('SERVER RESPONSE: %s', server_response)
            self.app.logger.debug('%s', server_response.to_string())
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
            using the :py:mod:`openpnpy.services` module
        :rtype: xml.etree.ElementTree.Element
        :raises NotImplementedError: To be implemented by user subclass
        """
        raise NotImplementedError

    def handle_work_response(self, work_response):
        """What to do when a PnP agent sends a work response.

        :param work_response: Work response sent by the PnP agent
        :type work_response: openpnpy.server.PnpMessage
        :return: Body element to be used in the repsonse message, as can be built 
            using the :py:mod:`openpnpy.services` module
        :rtype: xml.etree.ElementTree.Element
        :raises NotImplementedError: To be implemented by user subclass
        """
        raise NotImplementedError
