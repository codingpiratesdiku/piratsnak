#!/usr/bin/env python3

import sys
import socket
import selectors

class Server:
    def __init__(self, port: int):
        self.port = port

    def log(self, message: str):
        print(message, file=sys.stderr)

    def log_current_connections(self):
        self.log(f'current connections: {[conn.getpeername() for conn in self.connections]}')

    def serve(self):
        self.log('serving')
        self.selector = selectors.DefaultSelector()
        self.connections = set()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.port))
            sock.listen(100)
            sock.setblocking(False)

            self.selector.register(sock, selectors.EVENT_READ, self.accept)
            while True:
                events = self.selector.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

    def close(self):
        self.log('closing all connections')
        for conn in self.connections:
            self.selector.unregister(conn)
            conn.close()

        self.connections = set()
        self.selector = None

    def accept(self, sock, mask):
        conn, addr = sock.accept()
        self.log(f'accepted {conn.getpeername()}')
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read)
        self.connections.add(conn)
        self.log_current_connections()

    def read(self, conn, mask):
        data = conn.recv(1024)
        if data:
            for other_conn in self.connections:
                if other_conn != conn:
                    self.log(f'sending {repr(data)} from {conn.getpeername()} to {other_conn.getpeername()}')
                    other_conn.send(data)
        else:
            self.log(f'closing {conn.getpeername()}')
            self.connections.remove(conn)
            self.log_current_connections()
            self.selector.unregister(conn)
            conn.close()

if __name__ == '__main__':
    server = Server(port=50008)
    try:
        server.serve()
    except KeyboardInterrupt:
        server.close()
