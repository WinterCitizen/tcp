from io import BytesIO


class SocketDummy:
    def __init__(self, port):
        self.port = port

    def getsockname(self):
        return None, self.port


class IOStreamDummy:
    def __init__(self, port, content):
        self.buffer = BytesIO(content)
        self.socket = SocketDummy(port)

    async def read_bytes(self, amount=1):
        return self.buffer.read(amount)

    async def write_bytes(self, content):
        result = self.buffer.write(content)
        self.buffer.seek(0)

        return result
