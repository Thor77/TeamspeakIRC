import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron
from teamspeak_web_utils import latest_version


@irc3.plugin
class TSVersion(object):
    def __init__(self, bot):
        self.bot = bot
        self.client_version = None
        self.server_version = None
        config = bot.config.get('tsversion', {})
        self.channel = config.get('channel')
        self.topic_template = config.get(
            'topic',
            'Client: {client} Server: {server}'
        )

    @cron('1 * * * *')
    def fetch_version(self):
        new_client, new_server = latest_version()
        if self.channel:
            # Notify channel
            if self.client_version is not None and \
                    self.client_version != new_client:
                self.bot.privmsg(self.channel,
                                 'New client release: {}'.format(new_client))

            if self.server_version is not None and \
                    self.server_version != new_server:
                self.bot.privmsg(self.channel,
                                 'New server release: {}'.format(new_server))

        self.client_version = new_client
        self.server_version = new_server

    @command(permission='view')
    def tsversion(self, mask, target, args):
        '''Check latest Teamspeak3 Server/Client-version

            %%tsversion
        '''
        if not self.client_version or not self.server_version:
            self.fetch_version()
        return 'Client: {} Server: {}'.format(
            self.client_version, self.server_version)

    @command(permission='admin')
    def topic(self, mask, target, args):
        '''Set topic to contain Teamspeak3 Server/Client-version

            %%topic
        '''
        if not self.client_version or not self.server_version:
            self.fetch_version()
        if self.channel and self.topic_template:
            topic = self.topic_template.format(
                client=self.client_version, server=self.server_version
            )
            self.bot.topic(self.channel, topic)
