from tornado.tcpserver import TCPServer as BaseTCPServer
from tornado.iostream import StreamClosedError
from tornado.ioloop import IOLoop
from messages import SourceMessageProcessor

SOURCES_PORT = 8888
LISTENERS_PORT = 8889


class TCPServer(BaseTCPServer):
    sources = {}
    listeners = {}

    def get_connection_port(self, stream):
        address, port = stream.socket.getsockname()

        return port

    def register_source(self, stream, address):
        self.sources[address] = dict(stream=stream)

    def forget_source(self, address):
        self.sources.pop(address)

    async def sources_handler(self, stream, address):
        self.register_source(stream, address)
        processor = SourceMessageProcessor(stream)

        try:
            while True:
                message = await processor.get_message(stream)
        except StreamClosedError:
            pass
        finally:
            self.forget_source(address)

    def register_listener(self, stream, address):
        self.listeners[address] = dict(stream=stream)

    def forget_listener(self, address):
        self.listeners.pop(address)

    async def listeners_handler(self, stream, address):
        self.register_listener(stream, address)

    async def handle_stream(self, stream, address):
        connection_port = self.get_connection_port(stream)

        if connection_port == SOURCES_PORT:
            return await self.sources_handler(stream, address)
        elif connection_port == LISTENERS_PORT:
            return await self.listeners_handler(stream, address)
        else:
            raise ValueError(
                f'Expected connection on either {LISTENERS_PORT} '
                f'or {SOURCES_PORT} ports. Recieved {connection_port}')

    # async def handle_stream(self, stream, address):
    #     while True:
    #         try:
    #             data = await stream.read_until(b"\n")
    #             await stream.write(data)
    #         except StreamClosedError:
    #             break


if __name__ == '__main__':
    server = EchoServer()
    server.bind(SOURCES_PORT)
    server.bind(LISTENERS_PORT)
    server.start()
    IOLoop.current().start()
