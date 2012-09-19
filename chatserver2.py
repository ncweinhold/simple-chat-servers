"""
Concurrent TCP Chat Server example using gevent.

Connect to this server using Telnet.
"""

__author__ = 'Nick Weinhold'

import gevent
import optparse
from gevent.server import StreamServer

class ChatServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.users = {}
        self.server = StreamServer((self.host, self.port), self.handle_chat)

    def serve_forever(self):
        self.server.serve_forever()

    def set_user_name(self, socket, fileobj):
        while True:
            data = fileobj.readline().strip()
            if data not in self.users:
                break
            else:
                fileobj.write('That display name is already in use.\n')
                fileobj.write('Please enter a display name: ')
                fileobj.flush()
        return data

    def handle_chat(self, socket, address):
        print ('New connection from %s:%s' % address)
        socket.sendall('Please enter a display name: ')
        fileobj = socket.makefile()
        name = self.set_user_name(socket, fileobj)
        self.users[name] = fileobj
        self.broadcast_join_message(name)
        while True:
            line = fileobj.readline()
            if not line:
                print ('Client disconnected')
                break
            if line.strip().lower() == 'quit':
                print ('Client quit')
                break
            self.broadcast_message(name, '%s said: %s' % (name, line))
        del self.users[name]
        self.broadcast_quit_message(name)

    def broadcast_message(self, name, msg):
        for user, fileobj in self.users.items():
            if user != name:
                fileobj.write(msg)
                fileobj.flush()

    def broadcast_quit_message(self, name):
        self.broadcast_message(name, '%s has just left the chat.\n' % name)

    def broadcast_join_message(self, name):
        self.broadcast_message(name, '%s has just joined the chat.\n' % name)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option(
            '-p', '--port', dest='port', type='int', default=12345,
            help='Specifies the port to listen on. Default is 12345')

    parser.add_option(
            '-n', '--host', dest='host', default='localhost',
            help='Hostname or the IP address. Default is localhost')

    options, args = parser.parse_args()

    try:
        print 'Starting server on %s:%s' % (options.host, options.port)
        server = ChatServer(options.host, options.port)
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print 'Exiting...'

