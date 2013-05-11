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
import urllib

class ParserError(Exception):
    pass

class ParserBase(object):
    
    def request(self, body):
        raise ParserError('request() must be extended by parser implementations')
    
    def response(self, body):
        raise ParserError('response() must be extended by parser implementations')

class NullParser(ParserBase):
    
    def request(self, body):
        return body
    
    def response(self, body):
        return body

class EncodedUpJsonDown(ParserBase):
    
    def request(self, body):
        try:
            return urllib.urlencode(body)
        except (ValueError, TypeError):
            raise ParserError('unable to serialise request body into URL encoded')
    
    def response(self, body):
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            raise ParserError('unable to deserialise response body from JSON')

class JsonUpJsonDown(ParserBase):
    
    def request(self, body):
        try:
            return json.dumps(body)
        except (ValueError, TypeError):
            raise ParserError('unable to serialise request body into JSON')
    
    def response(self, body):
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            raise ParserError('unable to deserialise response body from JSON')

'''

    eof

'''
