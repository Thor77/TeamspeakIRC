from irc3.plugins.command import command
from irc3.plugins.cron import cron
import irc3

from teamspeak_web_utils import nplstatus


@irc3.plugin
class TS3NPL(object):
    def __init__(self, bot):
        self.bot = bot
        self.npl_status = None
        config = bot.config.get('ts3npl', {})
        self.target_channel = config.get('channel')
        self.message_template = config.get(
            'template', 'NPL-Registrations are {announcement} {status}!'
        )

    @cron('* * * * *')
    def fetch_status(self):
        print('checking status')
        new_status = nplstatus()
        if self.npl_status is not None and new_status != self.npl_status \
                and self.target_channel:
            if new_status:
                self.bot.privmsg(
                    self.target_channel,
                    self.message_template.format(
                        announcement='now', status='open'
                    )
                )
            else:
                self.bot.privmsg(
                    self.target_channel,
                    self.message_template.format(
                        announcement='now', status='closed'
                    )
                )
        self.npl_status = new_status

    @command(permission='view')
    def nplstatus(self, mask, target, args):
        '''check Teamspeak3 NPL-Registration-status

            %%nplstatus
        '''
        if self.npl_status is None:
            self.npl_status = nplstatus()

        if self.npl_status:
            return self.message_template.format(
                announcement='currently', status='open')
        else:
            return self.message_template.format(
                announcement='currently', status='closed')
