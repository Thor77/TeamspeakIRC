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
        key = args['<item>']
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
        if args['<item>'] in self.bot.db[self]:
            del self.bot.db[self][args['<item>']]
            return 'Successfully removed {} from bar!'.format(args['<item>'])
        else:
            return 'Bar doesn\'t contain this item!'

    @command
    def bar(self, mask, target, args):
        '''get all items in bar or return specific value

            %%bar [<item>]
        '''
        if self in self.bot.db:
            item = args['<item>']
            if item is not None:
                # get specific argument
                if item in self.bot.db[self]:
                    return self.bot.db[self][item]
                else:
                    return 'My bar doesn\'t contain this item!'
            else:
                # list bar
                keys = self.bot.db[self].keys()
                if len(keys) >= 1:
                    return ', '.join(keys)
        return 'No items in bar!'
