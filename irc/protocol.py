import socket
import logging
from threading import Thread

log = logging.getLogger()
log.setLevel(logging.DEBUG)
# define handlers
file_handler = logging.FileHandler('log.txt', 'w', 'UTF-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s', '%H:%M:%S'))
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
# add handlers
log.addHandler(file_handler)
log.addHandler(stream_handler)

class Connection:

    def __init__(self):
        # vars
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # calls

    def connect(self, ip, port):
        self.sock.connect((ip, port))
        self.sock.setblocking(False)
        log.info('Successfully connected to %s:%s!', ip, port)

    def close_socket(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        log.debug('Closed socket!')

    def send(self, line):
        self.sock.send((line + '\r\n').encode('UTF-8', errors='ignore'))
        log.debug('>>' + line)

    def read(self, size, wait=False):
        raw = self.sock.recv(size).decode('UTF-8', errors='ignore')
        if wait:
            while len(raw) == 0:
                raw = self.sock.recv(size).decode('UTF-8', errors='ignore')
        return raw

class Basic(Connection):

    def __init__(self):
        Connection.__init__(self)

    def disconnect(self):
        self.close_socket()
        log.info('Disconnected!')

    def pong(self, ping):
        self.send('PONG :{0}'.format(ping))

    def quit(self, quitmsg=None):
        if quitmsg:
            self.send('QUIT :{0}'.format(quitmsg))
        else:
            self.send('QUIT')

    def nick(self, nickname):
        self.send('NICK {0}'.format(nickname))

    def user(self, username, hostname, servername, realname):
        self.send('USER {0} {1} {2} :{3}'.format(username, hostname, servername, realname))

    def join(self, channel):
        self.send('JOIN {0}'.format(channel))

    def part(self, channel):
        self.send('PART {0}'.format(channel))

    def privmsg(self, msg, reciever):
        self.send('PRIVMSG {0} :{1}'.format(reciever, msg))

    def notice(self, msg, reciever):
        self.send('NOTICE {} :{}'.format(reciever, msg))

    def topic(self, channel, topic=None):
        if topic:
            self.send('TOPIC {} :{}'.format(channel, topic))
        else:
            self.send('TOPIC {}'.format(channel))