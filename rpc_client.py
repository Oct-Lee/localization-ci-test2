import time
from threading import Event
from typing import Optional
from xmlrpc.client import ServerProxy

from unitxutils import formatted_logging

logger = formatted_logging.logging.getLogger(__name__)


class RPCClient(ServerProxy):
    """
    RPC client for connecting to the RPC server.
    Inputs:
    - port: int, port number to connect to.
    - timeout: Optional[float], timeout for connection.
    - allow_none: bool, allow None values to be sent over the connection to the server.
    """

    def __init__(
        self, port: int, timeout: Optional[float] = None, allow_none: bool = False
    ):
        uri = "http://127.0.0.1:%d" % port
        ServerProxy.__init__(self, uri, allow_none=allow_none)
        self.should_quit = Event()
        start = time.time()
        while not self.should_quit.is_set():
            try:
                assert self.rpc_ready(), "rpc server not ready"
                logger.info(f"rpc client on: {uri}")
                break
            except ConnectionRefusedError as e:
                logger.error("failed to connect to %s. retrying in 1 sec" % uri)
                if (timeout is not None) and ((time.time() - start) > timeout):
                    raise e
                time.sleep(1)

    def cleanup(self):
        self.should_quit.set()
        self.__exit__()

    def __getstate__(self):
        pass

    def __setstate__(self, state):
        pass

