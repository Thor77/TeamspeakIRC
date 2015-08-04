from irc.protocol import log

subscriptions = {}

def subscribe(event, func):
    l = subscriptions.setdefault(event, [])
    if not func in l:
        l.append(func)
        log.debug('{} subscribed to {}!'.format(func, event))

def fire(event, *args, **kwargs):
    for func in subscriptions.get(event, []):
        log.debug('fired {} by event {}!'.format(func, event))
        func(*args, **kwargs)

def channel_msg(func):
    '''
    fired on channel-message
    args: bot, host, target, msg
    '''
    subscribe('channel_msg', func)

def query_msg(func):
    '''
    fired on query-message
    args: bot, host, msg
    '''
    subscribe('query_msg', func)

def user_join(func):
    '''
    fired when a user joins the bots channel
    args: host
    '''
    subscribe('user_join', func)

def user_part(func):
    '''
    fired when a user parts from the bots channel
    args: host
    '''
    subscribe('user_part', func)

def connected(func):
    '''
    fired after MOTD or END OF MOTD
    args: bot
    '''
    subscribe('connected', func)

def disconnected(func):
    '''
    fired before disconnecting
    args: bot
    '''
    subscribe('disconnected', func)