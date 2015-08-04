from irc.bot import IRCBot
import irc.events
import irc.loops
from irc.protocol import log
import time
from datetime import timedelta, datetime
import sqlite3
import nplstatus

ip = 'irc.quakenet.org'
port = 6667
nick = 'TSBot'
channel = '#teamspeak'

start_time = time.time()

db = sqlite3.connect('bar.db')
db_cursor = db.cursor()
db_cursor.execute('CREATE TABLE IF NOT EXISTS bar (trigger text, answer text)')
db_cursor.execute('CREATE TABLE IF NOT EXISTS lowscore (username text, lines text, time int)')
db.commit()

global last_status
last_status = nplstatus.get()


# functions for the bar-functionality
def add_to_bar(trigger, answer):
    db_cursor.execute('INSERT INTO bar VALUES (?, ?)', (str(trigger.lower()), str(answer)))
    db.commit()


def remove_from_bar(trigger):
    db_cursor.execute('DELETE FROM bar WHERE trigger=?', (trigger.lower(),))
    db.commit()


def get_triggers():
    r = []
    for trigger in db_cursor.execute('SELECT trigger FROM bar'):
        r.append(trigger[0])
    return r


def get_text(trigger):
    db_cursor.execute('SELECT answer FROM bar WHERE trigger=?', (trigger,))
    return db_cursor.fetchone()[0]

# variables for lowscore-functionality
lowscore_last_messages = {}

# functions for the lowscore-functionality
def add_lowscore(username, lines, time):
    db_cursor.execute('INSERT INTO lowscore VALUES (?,?,?)', (str(username), str(lines), int(time)))
    db.commit()

def get_lowscores(amount):
    r = []
    for lowscore in db_cursor.execute('SELECT * from lowscore ORDER BY time ASC LIMIT '+str(amount)):
        r.append({'username': lowscore[0], 'lines': lowscore[1], 'time': lowscore[2]})
    return r

@irc.loops.min5
def check_status(bot):
    global last_status
    status = nplstatus.get()
    if status != last_status:
        last_status = status
        if status:
            bot.privmsg('NPL-Registrations are now open! http://npl.teamspeakusa.com/ts3npl.php')
        else:
            bot.privmsg('NPL-Registrations are now closed!')


@irc.events.channel_msg
def lowscore_message(bot, host, target, msg):
    user = lowscore_last_messages.get(host, None)
    if user is not None:
        user['lines'].append(msg)

    if msg.startswith('_lowscore'):
        lowscores = get_lowscores(3)
        answer = 'TOP 3: '
        for l in lowscores:
            answer += l['username'] + ' [T: ' + str(l['time']) + ' seconds] '
        bot.privmsg(answer)

@irc.events.user_join
def lowscore_user_join(bot, host):
    global lowscore_last_messages
    lowscore_last_messages[host] = {'lines': [], 'join': time.time()}

@irc.events.user_part
def lowscore_user_part(bot, host):
    user = lowscore_last_messages.get(host, None)
    if user is not None:
        join_time = user['join']
        cur_time = time.time()
        if (cur_time - join_time) < 10*60 and len(user['lines']) > 0:
            add_lowscore(host.split('!')[0], user['lines'], cur_time-join_time)   

        lowscore_last_messages.pop(host, None)

@irc.loops.min5
def lowscore_cleanup(bot):
    global lowscore_last_messages
    cur_time = time.time()
    to_del = []
    for key in lowscore_last_messages:
        if (cur_time - lowscore_last_messages[key]['join']) > 10*60:
            to_del.append(key)
    for key in to_del:
        lowscore_last_messages.pop(key, None)

@irc.events.channel_msg
def info(bot, host, target, msg):
    msg = msg.lower()
    if nick.lower() in msg:
        if 'who are you' in msg or 'who is' in msg or 'what are you doing' in msg:
            bot.privmsg('I\'m a bot fetching the status of NPL-Registrations every 5 minutes! You can check it manually with "!nplstatus".')
        elif 'how are you' in msg:
            sec = timedelta(seconds=(time.time() - start_time))
            d = datetime(1, 1, 1) + sec
            days = d.day - 1
            hours = d.hour
            minutes = d.minute
            seconds = d.second
            bot.privmsg('I\'m fine and running for {} days, {} hours, {} minutes and {} seconds!'.format(days, hours, minutes, seconds))


@irc.events.channel_msg
def commands(bot, host, target, msg):
    nick = host.split('!')[0]
    msg_ = msg
    msg = msg.lower()
    if msg.startswith('!'):
        cmd = msg[1:].strip()
        cmd_ = msg_[1:].strip()
        if cmd == 'register':
            bot.notice(add_register(nick), nick)
        elif cmd == 'unregister':
            bot.notice(remove_register(nick), nick)
        elif cmd == 'nplstatus':
            if last_status:
                bot.privmsg('NPL-Registrations are open! You can register one here: http://npl.teamspeakusa.com/ts3npl.php')
            else:
                bot.privmsg('NPL-Registrations are closed!')
        elif cmd == 'bar':
            triggers = get_triggers()
            if len(triggers) >= 1:
                bot.privmsg(', '.join(triggers))
            else:
                bot.privmsg('No items in bar!')
        elif cmd.split()[0] == 'addtobar':
            cmd_split = cmd_.split()
            if len(cmd_split) < 3:
                bot.privmsg('Too less arguments! Try "!addtobar <trigger> <message>"')
            else:
                if cmd_split[1].lower() not in get_triggers():
                    add_to_bar(cmd_split[1].lower(), ' '.join(cmd_split[2:]))
                    bot.privmsg('Successfully added {} to bar!'.format(cmd_split[1].lower()))
                else:
                    bot.privmsg('Item already in bar!')
        elif cmd.split()[0] == 'removefrombar':
            cmd_split = cmd_.split()
            if len(cmd_split) < 2:
                bot.privmsg('Too less arguments! Try "!removefrombar <trigger>"')
            else:
                if cmd_split[1].lower() in get_triggers():
                    remove_from_bar(cmd_split[1].lower())
                    bot.privmsg('Successfully removed {} from bar!'.format(cmd_split[1].lower()))
                else:
                    bot.privmsg('Item not in bar!')


@irc.events.channel_msg
def bar(bot, host, target, msg):
    if msg.startswith('!'):
        msg = msg.lower()[1:]
        triggers = get_triggers()
        if msg in triggers:
            bot.privmsg(get_text(msg))


@irc.events.connected
def join_channels(bot):
    bot.join(channel)

bot = IRCBot(ip, port, nick)
bot.start()
