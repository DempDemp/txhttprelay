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

from base64 import b64encode

class AuthenticationError(Exception):
    pass

class AuthenticationBase(object):
    
    AUTHNAME = 'undefined authentication'
    
    def __unicode__(self):
        return u'<Authentication ({})>'.format(self.AUTHNAME)
    
    def __str__(self):
        return self.__unicode__()
    
    def apply_auth(self, request=None):
        raise AuthenticationError('apply_auth() must be extended by authentication implementations')

class NullAuth(AuthenticationBase):
    
    AUTHNAME = 'null'
    
    def apply_auth(self, request=None):
        return request

class HttpBasicAuth(AuthenticationBase):
    
    AUTHNAME = 'basic HTTP'
    
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
    
    def _get_auth_header(self):
        b = '{}:{}'.format(self.username, self.password)
        return 'Basic {}'.format(b64encode(b))
    
    def apply_auth(self, request=None):
        request.set_header('Authorization', self._get_auth_header())
        return request

'''

    eof

'''
