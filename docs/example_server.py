# myserver.py

#!/usr/bin/env python3

from openpnpy.server import PnpServer
from openpnpy.messages import device_info, backoff

class MyServer(PnpServer):

    def handle_work_request(self, work_request):
        return device_info(type='all')

    def handle_work_response(self, work_response):
        return backoff(seconds=30)

server = MyServer(__name__)

if __name__ == '__main__':
    server.run(host='0.0.0.0', port='1234')
