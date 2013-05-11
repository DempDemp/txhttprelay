LISTEN_PORT = 9876
LISTEN_HOST = '127.0.0.1'
LISTEN_SOCKET = 'relay.sock'

USE = 'tcp' # 'tcp' or 'unix' to toggle which of the above to use

REQUESTS = {}

try:
    from local_config import *
except ImportError:
    import sys
    sys.stderr.write('unable to import local_config')
    sys.exit(1)
