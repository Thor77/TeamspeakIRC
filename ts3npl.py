from irc3.plugins.command import command
from irc3.plugins.cron import cron
import irc3

import nplstatus


@irc3.plugin
class TS3NPL(object):
    def __init__(self, bot):
        self.bot = bot
        self.npl_status = None
        self.target_channel = '#teamspeak'

    @cron('* * * * *')
    def fetch_status(self):
        print('checked cron')
        new_status = nplstatus.get()
        if self.npl_status is not None and new_status != self.npl_status:
            if new_status:
                self.bot.privmsg(self.target_channel,
                                 'NPL-Registrations are now open!')
            else:
                self.bot.privmsg(self.target_channel,
                                 'NPL-Registrations are now closed!')
        self.npl_status = new_status

    @command(permission='view')
    def nplstatus(self, mask, target, args):
        '''check Teamspeak3 NPL-Registration-status

            %%nplstatus
        '''
        if self.npl_status is None:
            self.npl_status = nplstatus.get()

        if self.npl_status:
            return 'NPL-Registrations are currently open!'
        else:
            return 'NPL-Registrations are currently closed!'
