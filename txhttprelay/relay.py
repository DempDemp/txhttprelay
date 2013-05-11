'''

    Copyright 2012 Joe Harris

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

import time
import json
from string import Formatter

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver

from txhttprelay.auth import NullAuth
from txhttprelay.parser import NullParser
from txhttprelay.transport import HttpRequest, HttpTransport

class RelayProtocol(LineOnlyReceiver):
    
    MAX_LENGTH = 65536
    
    def __init__(self, factory):
        self.factory = factory
        self._ids = set()
        self._format = Formatter()
    
    def error(self, s):
        return self.reply({
            'id': 0,
            'state': 'error',
            'message': s
        })
    
    def reply(self, msg={}):
        try:
            self.transport.write(json.dumps(msg) + self.delimiter)
            return True
        except (ValueError, TypeError):
            return self.error('unable to serialise response (internal error)')
    
    def parse(self, line):
        try:
            deserialised = json.loads(line)
        except (ValueError, TypeError):
            return self.error('unable to deserialise request (client error)')
        if 'request' not in deserialised:
            return self.error('missing required parameter: request')
        if 'id' not in deserialised:
            return self.error('missing required parameter: id')
        id = deserialised.get('id', '')
        request = deserialised.get('request', '')
        params = deserialised.get('params', {})
        data = deserialised.get('data', {})
        request_config = self.factory.get_request(request)
        if not request_config:
            return self.error('not a valid request: {}'.format(request))
        if len(request_config) != 5:
            return self.error('request tuple does not have three elements: {}'.format(request))
        request_method, request_url, expected_status, request_auth, parser = request_config
        if not request_auth:
            request_auth = NullAuth()
        if not parser:
            parser = NullParser()
        for (lit, field, spec, conv) in self._format.parse(request_url):
            if field and field not in params:
                return self.error('missing required parameter: {}'.format(field))
        try:
            parsed_url = request_url.format(**params)
        except KeyError:
            return self.error('unable to parse request url with provided paramters')
        self.send_request(
            id=id,
            method=request_method,
            url=parsed_url,
            auth=request_auth,
            data=data,
            expected=expected_status,
            parser=parser
        )
    
    def send_request(self, id='', method='GET', url='', auth=None, data='', expected=200, parser=None):
        request = HttpRequest(
            id=id,
            method=method,
            url=url,
            expected=expected,
            parser=parser
        )
        if data:
            request.set_body(data)
        request = auth.apply_auth(request)
        HttpTransport(request).go(self.got_response)
        self.reply({
            'id': str(request.id),
            'status': 'dispatched',
        })
    
    def got_response(self, response):
        self.reply({
            'id': response.request.id,
            'status': 'ok' if response.ok() else 'error',
            'response': response.data(),
            'time': round(time.time() - response.request.start_time, 5),
        })
    
    def lineReceived(self, line):
        self.parse(line)

class RelayFactory(Factory):
    
    protocol = RelayProtocol
    
    def __init__(self, config):
        self.requests = config.REQUESTS
    
    def get_request(self, request=''):
        return self.requests.get(request, None)
    
    def buildProtocol(self, addr):
        return self.protocol(self)

'''

    eof

'''
