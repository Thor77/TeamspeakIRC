import time
import sys
import threading
from irc.protocol import Basic, log
import irc.events
import irc.loops
import traceback

class IRCBot(Basic):

    def __init__(self, ip, port, nickname):
        # vars
        Basic.__init__(self)
        self.nickname = nickname
        self.current_channel = None
        self.queue = []
        self.loop_threads = []
        # calls
        self.connect(ip, port)
        self.nick(nickname)
        self.user(nickname, nickname, nickname, nickname)

    def start_loop_threads(self):
        for event in irc.loops.events:
            if irc.loops.has_subscribers(event):
                log.debug('started thread for loop {}'.format(event))
                t = LoopThread(irc.loops.events[event], event, self)
                t.start()
                self.loop_threads.append(t)

    def stop_loop_threads(self):
        for t in self.loop_threads:
            t.stop()
            t.join

    def start(self):
        log.info('Mainloop started!')
        self.start_loop_threads()
        try:
            for line in self.recieve_line():
                log.debug('<<' + line)
                self.parse_line(line)
        except KeyboardInterrupt:
            self.stop_loop_threads()
            self.disconnect('Interrupted')
        except ConnectionResetError:
            self.stop_loop_threads()
            log.critical('connection reset by peer')

    def recieve_line(self):
        buff = ''
        while True:
            try:
                buff += self.read(4096)
                while '\n' in buff:
                    line, buff = buff.split('\n', 1)
                    yield line.strip()
            except BlockingIOError:
                pass
            self.send_queue()
            time.sleep(0.25)
        return

    def parse_line(self, line):
        # split the line and handle ping
        parts = line.split(' ')
        if parts[0][0] != ':':
            self.handle_not_host(parts[0], parts[1:])
            return
        host = parts[0][1:]
        event = parts[1]
        target = parts[2]
        if len(parts) < 4:
            msg = ''
        else:
            msg = ' '.join(parts[3:])[1:]
        self.handle_line(host, event, target, msg)
    
    def handle_line(self, host, event, target, msg):
        if any(x.isdigit() for x in event):
            self.handle_event_number(host, int(event), target, msg)
        else:
            self.handle_event_str(host, event, target, msg)

    def handle_event_number(self, host, event, target, msg):
        if event == 376 or event == 422:
            irc.events.fire('connected', self)

    def handle_event_str(self, host, event, target, msg):
        if event == 'PRIVMSG':
            if target[0] == '#':
                # channelmsg
                irc.events.fire('channel_msg', self, host, target, msg)
            else:
                # querymsg
                irc.events.fire('query_msg', self, host, msg)
        elif event == 'JOIN':
            if host.split('!')[0] != self.nickname:
                irc.events.fire('user_join', self, host)
        elif event == 'PART' or event == 'QUIT':
            if host.split('!')[0] != self.nickname:
                irc.events.fire('user_part', self, host)
    
    def handle_not_host(self, not_host, parts):
        type_ = not_host
        parts[0] = parts[0][1:]
        msg = ' '.join(parts)
        if type_ == 'ERROR':
            if msg == 'Your host is trying to (re)connect too fast -- throttled':
                log.critical('Reconnecting too fast!')
                self.disconnect()
            elif msg.startswith('Closing Link'):
                log.critical('Server closed link!')
                self.disconnect()
        elif type_ == 'PING':
            self.pong(msg)

    # override methods
    def send(self, line):
        self.queue.append(line)

    def send_queue(self):
        for line in self.queue:
            Basic.send(self, line)
        self.queue = []

    def disconnect(self, quitmsg=None):
        irc.events.fire('disconnected', self)
        self.quit(quitmsg)
        # send queue (to prevent "EOF from client")
        self.send_queue()
        Basic.disconnect(self)

    def join(self, channel):
        Basic.join(self, channel)
        self.current_channel = channel
        log.info('Joined {}'.format(channel))

    def privmsg(self, msg, reciever=None):
        if not reciever:
            reciever = self.current_channel
        Basic.privmsg(self, msg, reciever)

    def topic(self, topic, channel=None):
        if not channel:
            channel = self.current_channel
        Basic.topic(self, channel, topic)

class LoopThread(threading.Thread):

    def __init__(self, delay, event, bot):
        threading.Thread.__init__(self)
        self.daemon = True
        self.delay = delay
        self.event = event
        self.event_crashed = event + '_crashed'
        self.bot = bot
        self.e = threading.Event()

    def run(self):
        while not self.e.wait(self.delay):
            try:
                irc.loops.fire(self.event, self.bot)
            except:
                log.critical('error in "' + self.event + '"-thread!')
                log.critical('-----')
                log.critical(traceback.format_exc())
                log.critical('-----')

    def stop(self):
        self.e.set()