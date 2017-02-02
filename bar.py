from irc3.plugins.command import command
import irc3


@irc3.plugin
class Bar(object):
    def __init__(self, bot):
        self.bot = bot

    @command(permission='admin')
    def addtobar(self, mask, target, args):
        '''add <item> with <text> to bar

            %%addtobar <item> <text>...
        '''
        key = args['<item>'].lower()
        value = ' '.join(args['<text>'])
        if self in self.bot.db:
            self.bot.db[self][key] = value
        else:
            self.bot.db[self] = {key: value}
        return 'Successfully added {} to bar!'.format(key)

    @command(permission='admin')
    def removefrombar(self, mask, target, args):
        '''remove <item> from bar

            %%removefrombar <item>
        '''
        if self not in self.bot.db:
            return 'No items in bar!'
        item = args['<item>'].lower()
        if item in self.bot.db[self]:
            del self.bot.db[self][item]
            return 'Successfully removed {} from bar!'.format(item)
        else:
            return 'Bar doesn\'t contain this item!'

    @command
    def bar(self, mask, target, args):
        '''get all items in bar
            if you want to access an specific item, use _<item>
            or if you want to "give" an item to a user use !give <nick> <item>

            %%bar
        '''
        if self in self.bot.db:
            # list bar
            keys = self.bot.db[self].keys()
            if len(keys) >= 1:
                return ', '.join(keys)
        return 'No items in bar!'

    @command
    def give(self, mask, target, args):
        '''"give" an item to an specific user

            %%give <nick> <item>
        '''
        if self in self.bot.db and len(self.bot.db[self]) >= 1:
            item = args['<item>']
            if item in self.bot.db[self]:
                return '{}: {}'.format(args['<nick>'], self.bot.db[self][item])
            else:
                return 'Bar doesn\'t contain this item!'
        return 'No items in bar!'

    @irc3.event(irc3.rfc.PRIVMSG)
    def bar_get(self, mask=None, event=None, target=None, data=None):
        if data.startswith('?'):
            item = data.split()[0][1:]
            if item in self.bot.db.get(self, {}):
                self.bot.privmsg(target, self.bot.db[self][item])
