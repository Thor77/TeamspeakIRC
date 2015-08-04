from irc.protocol import log

events = {'sek1': 1, 'sek5': 5, 'sek30': 30, 'min1': 60, 'min5': 300, 'min30': 1800, 'h1': 3600, 'h12': 43200, 'd1': 86400}
subscriptions = {}

def subscribe(event, func):
    l = subscriptions.setdefault(event, [])
    if not func in l:
        l.append(func)
        log.debug('{} subscribed to loop {}!'.format(func, event))

def fire(event, *args, **kwargs):
    for func in subscriptions.get(event, []):
        func(*args, **kwargs)
        log.debug('fired {} by loop {}!'.format(func, event))

def has_subscribers(event):
	return bool(subscriptions.get(event, []))

def sek1(func):
	subscribe('sek1', func)

def sek1_crashed(func):
	subscribe('sek1_crashed', func)

def sek5(func):
	subscribe('sek5', func)

def sek5_crashed(func):
	subscribe('sek5_crashed', func)

def sek30(func):
	subscribe('sek30', func)

def sek30_crashed(func):
	subscribe('sek30_crashed', func)

def min1(func):
	subscribe('min1', func)

def min1_crashed(func):
	subscribe('min1_crashed', func)

def min5(func):
	subscribe('min5', func)

def min5_crashed(func):
	subscribe('min5_crashed', func)

def min30(func):
	subscribe('min30', func)

def min30_crashed(func):
	subscribe('min30_crashed', func)

def h1(func):
	subscribe('h1', func)

def h1_crashed(func):
	subscribe('h1_crashed', func)

def h12(func):
	subscribe('h12', func)

def h12_crashed(func):
	subscribe('h12_crashed', func)

def d1(func):
	subscribe('d1', func)

def d1_crashed(func):
	subscribe('d1_crashed', func)