"""
Concurrent TCP Chat Server Example using Eventlet.

Connect to this server using Telnet.

"""

__author__ = 'Nick Weinhold'

import eventlet
import optparse
from eventlet.green import socket

class ChatServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = eventlet.listen((self.host, self.port))
        self.users = {}

    def serve_forever(self):
        while True:
            new_connection, address = self.server.accept()
            new_writer = new_connection.makefile('w')
            eventlet.spawn_n(self.handle_chat,
                    new_writer,
                    new_connection.makefile('r'))
        
    def set_user_name(self, writer, reader):
        while True:
            writer.write("Please enter a display name: ")
            writer.flush()
            name = reader.readline().strip()
            if name not in self.users:
                break
            else:
                writer.write("That display name is already in use.\n")
                writer.flush()
        return name

    def broadcast_message(self, w, msg):
        for user, writer in self.users.items():
            try:
                if writer is not w:
                    writer.write(msg)
                    writer.flush()
            except socket.error, e:
                if e[0] != 32:
                    raise

    def broadcast_join_message(self, writer, name):
        msg = "%s has just joined the chat.\n" % name
        self.broadcast_message(writer, msg)

    def broadcast_leave_message(self, writer, name):
        msg = "%s has just left the chat.\n" % name
        self.broadcast_message(writer, msg)
        del self.users[name]

    def handle_chat(self, writer, reader):
        name = self.set_user_name(writer, reader)
        self.users[name] = writer
        writer.write("Welcome %s\n" % name)
        writer.flush()
        self.broadcast_join_message(writer, name)
        line = reader.readline()
        while line:
            self.broadcast_message(writer, line)
            line = reader.readline()
        self.broadcast_leave_message(writer, name)

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
        print "Starting server on %s:%s" % (options.host, options.port)
        server = ChatServer(options.host, options.port)
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print "Exiting..."

