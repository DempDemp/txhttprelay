'''

    Copyright 2013 Joe Harris

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

from setuptools import setup, find_packages
from txhttprelay import __version__

setup(
    name='txhttprelay',
    version=__version__,
    url='https://github.com/meeb/txhttprelay',
    license='Apache 2.0',
    description='TCP and UNIX socket HTTP REST API relay',
    author='Joe Harris',
    author_email='j@m.pr',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
    ],
)

'''

    EOF

'''
