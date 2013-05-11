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

import json
import time
from urlparse import urlsplit, urlunsplit

from zope.interface import implements
from twisted.python import failure
from twisted.internet import reactor, protocol
from twisted.web.client import Agent
from twisted.web.iweb import IBodyProducer
from twisted.web.http_headers import Headers
from twisted.internet.defer import succeed

from txhttprelay.parser import ParserError

# try and import the verifying SSL context from txverifyssl
try:
    from txverifyssl.context import VerifyingSSLContext as SSLContextFactory
except ImportError:
    # if txverifyssl is not installed default to the built-in SSL context, this works but has no SSL verification
    from twisted.internet.ssl import ClientContextFactory
    class SSLContextFactory(ClientContextFactory):
        def getContext(self, hostname, port):
            return ClientContextFactory.getContext(self)

class RequestError(Exception):
    pass

class HttpRequest(object):
    
    METHODS = ('get', 'post', 'put', 'delete', 'head', 'options')
    
    def __init__(self, id='', method='', url='', expected=200, parser=None):
        method = method.lower().strip()
        if method not in self.METHODS:
            raise RequestError('invalid HTTP method: {}'.format(method))
        self.method = method
        self.url = urlsplit(url)
        self.expected = expected
        self.parser = parser
        self.headers = {}
        self.body = None
        self.set_header('User-Agent', 'txhttprelay')
        if self.method == 'post':
            self.set_header('Content-Type', 'application/x-www-form-urlencoded')
        self.id = id
        self.start_time = 0
    
    def __unicode__(self):
        return u'<HttpRequest ({} {})>'.format(
            self.method.upper(),
            urlunsplit(self.url)
        )
    
    def __str__(self):
        return self.__unicode__()
    
    def start_timer(self):
        self.start_time = time.time()
    
    def set_header(self, name, value):
        self.headers.setdefault(str(name), []).append(str(value))
    
    def set_body(self, body):
        if body:
            self.body = self.parser.request(body)

class HttpResponse(object):
    
    def __init__(self, request, code, headers, body):
        self.request = request
        self.code = int(code)
        self.headers = list(headers)
        self.body = str(body)
    
    def ok(self):
        return int(self.request.expected) == int(self.code)
    
    def data(self):
        if not self.request.parser:
            return self.body
        try:
            return self.request.parser.response(self.body)
        except ParserError:
            return None

class TransportError(Exception):
    pass

class StringProducer(object):
    
    implements(IBodyProducer)
    
    def __init__(self, data):
        self.body = data
        self.length = len(self.body)
    
    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)
    
    def pauseProducing(self):
        pass
    
    def stopProducing(self):
        pass

class StringReceiver(protocol.Protocol):
    
    def __init__(self, response, callback):
        self.response = response
        self.callback = callback
    
    def dataReceived(self, data):
        self.response.body += data
    
    def connectionLost(self, reason):
        self.callback(self.response)

class HttpTransport(object):
    
    def __init__(self, request):
        self.request = request
    
    def _request(self):
        method = self.request.method.upper()
        scheme = self.request.url.scheme.lower()
        if scheme == 'https':
            context = SSLContextFactory()
            if hasattr(context, 'set_expected_host'):
                context.set_expected_host(self.request.url.netloc)
            agent = Agent(reactor, context)
        elif scheme == 'http':
            agent = Agent(reactor)
        else:
            raise TransportError('only HTTP and HTTPS schemes are supported')
        producer = StringProducer(self.request.body) if self.request.body else None
        self.request.start_timer()
        return agent.request(
            method,
            urlunsplit(self.request.url),
            Headers(self.request.headers),
            producer
        )
    
    def go(self, callback=None):
        if not callback:
            raise TransportError('go() requires a callback as the only parameter')
        
        def _got_response(raw_response):
            if isinstance(raw_response, failure.Failure):
                error_body = json.dumps({'error':raw_response.getErrorMessage()})
                response = HttpResponse(request=self.request, code=0, headers={}, body=error_body)
                callback(response)
            else:
                response = HttpResponse(
                    request=self.request,
                    code=raw_response.code,
                    headers=raw_response.headers.getAllRawHeaders(),
                    body=''
                )
                raw_response.deliverBody(StringReceiver(response, callback))
        
        self._request().addBoth(_got_response)

'''

    eof

'''
