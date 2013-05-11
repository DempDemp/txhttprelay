import os.path
rundir = os.path.realpath(os.path.dirname(__file__))
os.chdir(rundir)

import sys
if rundir not in sys.path:
    sys.path.insert(0, rundir)

from twisted.application import service, internet

import config
from txhttprelay.relay import RelayFactory

application = service.Application('txhttprelay')
f = RelayFactory(config)

if config.USE == 'tcp':
    service = internet.TCPServer(config.LISTEN_PORT, f, interface=config.LISTEN_HOST)
elif config.USE == 'unix':
    service = internet.UNIXServer(config.LISTEN_SOCKET, f)
else:
    raise ValueError('config.USE must be one of "tcp" or "unix"')

service.setServiceParent(application)
