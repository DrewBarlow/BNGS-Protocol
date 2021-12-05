from src.request_handler import Handler
from socketserver import ThreadingTCPServer


class BNGS:
    def __init__(self, host: str="127.0.0.1", port: int=13037):
        self._server: ThreadingTCPServer = None
        self._HOST: str = host
        self._PORT: int = port

    def start_server(self) -> None:
        self._server = ThreadingTCPServer((self._HOST, self._PORT), Handler)
        print("BULLETIN IS READY TO RECEIVE.")
        self._server.serve_forever()
