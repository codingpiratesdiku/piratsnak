#!/usr/bin/env python3

import sys
import socket
import selectors
import threading
import os.path
import random
from typing import Callable

import urwid

host = 'localhost'
port = 50008

cat_info = '[INFO]'
cat_error = '[FEJL]'

class EditAndEnter(urwid.Edit):
    def __init__(self, add_message: Callable[[str], None], *args, **kwargs):
        super(EditAndEnter, self).__init__(*args, **kwargs)
        self.add_message = add_message

    def keypress(self, size, key: str):
        if key == 'enter':
            self.add_message(self.get_edit_text())
            self.set_edit_text('')
        elif key == 'page up':
            # TODO: Support scrolling.
            pass
        elif key == 'page down':
            # TODO: Support scrolling.
            pass
        else:
            return super(EditAndEnter, self).keypress(size, key)

class ServerCommunicator:
    def __init__(self, add_message: Callable[[str], None], server: str, port: int):
        self.add_message = add_message
        self.server = server
        self.port = port

    def setup(self):
        self.running = True

    def close(self):
        self.running = False
        self.selector.close()

    def send(self, message: str):
        if self.running:
            try:
                self.sock.sendall(message.encode('utf-8'))
            except BrokenPipeError:
                self.running = False
                self.add_message(f'[FEJL] Har mistet forbindelsen til {self.server}, kan ikke sende besked.')
                return
            self.add_message(message)
        else:
            self.add_message('[FEJL] Ikke forbundet, kan ikke sende besked.')

    def read(self, sock, mask):
        data = sock.recv(1024)
        if data:
            self.add_message(data.decode('utf-8'))

    def receive_messages(self):
        self.selector = selectors.DefaultSelector()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.sock = sock
            try:
                sock.connect((self.server, self.port))
            except ConnectionRefusedError:
                self.add_message(f'[FEJL] Kunne ikke forbinde til {self.server}.')
                self.running = False
                return
            self.selector.register(sock, selectors.EVENT_READ, self.read)
            while self.running:
                events = self.selector.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

class ClientInterface:
    def __init__(self, send_and_add_message: Callable[[str], None]):
        self.send_and_add_message = send_and_add_message

    def setup(self):
        # http://urwid.org/reference/display_modules.html#urwid.BaseScreen.register_palette_entry
        palette = [
            ('bold', 'default,bold', 'default'),
            ('info', 'dark blue', 'default'),
            ('error', 'light red', 'default'),
            ('name', 'light green', 'default'),
        ]
        prompt = '> '
        user_chat_message = EditAndEnter(self.send_and_add_message, ('bold', prompt))
        div = urwid.Divider()
        channel_info = urwid.Text(['Kanal: ', ('bold', 'piratsnak'), ' | Andre kanaler: '])
        self.chat_messages = urwid.Text('')
        widget = urwid.Filler(urwid.Pile([self.chat_messages, div, channel_info, user_chat_message]),
                              valign='bottom')

        self.urwid_loop = urwid.MainLoop(widget, palette)

    def run(self):
        self.urwid_loop.run()

    def set_messages(self, messages: list[str]):
        markups = []
        for message in messages:
            markups.append('\n')
            if message.startswith(cat_info):
                markups.append(('info', cat_info))
                markups.append(message[len(cat_info):])
            elif message.startswith(cat_error):
                markups.append(('error', cat_error))
                markups.append(message[len(cat_error):])
            else:
                try:
                    user_name, user_message = message.split(':', 1)
                    markups.append(('name', user_name))
                    markups.append(':' + user_message)
                except ValueError:
                    markups.append(message)
        self.chat_messages.set_text(markups[1:])

    def draw(self):
        self.urwid_loop.draw_screen()

    def stop(self):
        self.urwid_loop.stop()

class Client:
    def __init__(self, server: str, port: int, max_history: int, name: str):
        self.server_communicator = ServerCommunicator(self.add_message, server, port)
        self.client_interface = ClientInterface(self.handle_own_message)
        self.max_history = max_history
        self.name = name
        self.commands = {
            'exit': self.command_exit,
            'name': self.command_name
        }

    def connect(self):
        self.messages = []
        self.write_lock = threading.Lock()

        self.client_interface.setup()

        self.server_communicator.setup()
        self.receiver_thread = threading.Thread(
            target=self.server_communicator.receive_messages,
            daemon=True)
        self.receiver_thread.start()

        welcome_message = (
            f'Velkommen til piratsnak, {self.name}!',
            f'Du kan chatte med de andre ved at skrive en besked og trykke på Enter.',
            f'Skriv /name <dit navn> hvis du vil ændre dit navn fra {repr(self.name)} til noget andet.',
            f'Skriv /exit hvis du vil stoppe med at chatte.',
        )
        for line in welcome_message:
            self.add_message(f'{cat_info} {line}')

        self.client_interface.run()

    def command_exit(self):
        raise KeyboardInterrupt # Simulate Ctrl+C (not elegant, but easy)

    def command_name(self, new_name):
        self.name = new_name
        self.add_message(f'{cat_info} Dit nye navn: {self.name}')

    def handle_own_message(self, message: str):
        if message.startswith('/'):
            args = message[1:].split()
            try:
                command = self.commands[args[0]]
            except KeyError:
                self.add_message(f'{cat_error} Ukendt kommando {repr(args[0])}.')
                return
            command(*args[1:])
        else:
            self.server_communicator.send(f'{self.name}: {message}')

    def add_message(self, message: str):
        with self.write_lock:
            self.messages.append(message)
            if len(self.messages) > self.max_history:
                self.messages = self.messages[1:]
            self.client_interface.set_messages(self.messages)
            try:
                self.client_interface.draw()
            except Exception:
                pass

    def close(self):
        self.server_communicator.close()
        self.client_interface.stop()
        self.messages = []

def random_name():
    with open(os.path.join(os.path.dirname(__file__), 'blandede-dyr.txt')) as f:
        return random.choice(f.read().strip().split('\n'))

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 1:
        host = args[0]
    if len(args) >= 2:
        port = int(args[1])
    client = Client(server=host, port=port, max_history=100, name=random_name())
    try:
        client.connect()
    except KeyboardInterrupt:
        client.close()
