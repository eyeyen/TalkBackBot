#! /usr/bin/env python
# this is a scaffold for a multi network irc bot using the twisted framework

import re
import sys
import unicodedata
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import ssl
from twisted.python import log
from twisted.words.protocols import irc

################################################################################
########                        S e t t i n g s                         ########
################################################################################
identity = {
    'twistedbot': {
        'nickname': 'twistbot-',
        'realname': 'Twisted IRC Bot',
        'username': 'twistd',
        'nickserv_pw': None
    },
}
networks = {
    'Freenode': {
        'host': 'chat.eu.freenode.net',
        'port': 7000,
        'ssl': True,
        'identity': identity['twistedbot'],
        'autojoin': (
            '#channelname',
        )
    },
    'Teranetworks': {
        'host': 'irc.teranetworks.de',
        'port': 6697,
        'ssl': True,
        'identity': identity['twistedbot'],
        'autojoin': (
            '#woot',
        )
    }
}
################################################################################

class TwistedBot(irc.IRCClient):
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        print('twisted bot signed on')

        network = self.factory.network

        if network['identity']['nickserv_pw']:
            self.msg('NickServ', 
                'IDENTIFY %s' % network['identity']['nickserv_pw'])

        for channel in network['autojoin']:
            print('join channel %s' % channel)
            self.join(channel)

    def joined(self, channel):
        print('joined channel')

    def privmsg(self, user, channel, msg):
        print('[%s] <%s> %s' % (channel, user, msg))

    def alterCollidedNick(self, nickname):
        return nickname+'_'

    def _get_nickname(self):
        return self.factory.network['identity']['nickname']
    def _get_realname(self):
        return self.factory.network['identity']['realname']
    def _get_username(self):
        return self.factory.network['identity']['username']
    nickname = property(_get_nickname)
    realname = property(_get_realname)
    username = property(_get_username)

class TwistedBotFactory(protocol.ClientFactory):
    protocol = TwistedBot

    def __init__(self, network_name, network):
        self.network_name = network_name
        self.network = network

    def clientConnectionLost(self, connector, reason):
        print('client connection lost')
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('client connection failed')
        reactor.stop()

if __name__ == '__main__':
    for name in networks.keys():
        factory = TwistedBotFactory(name, networks[name])
        
        host = networks[name]['host']
        port = networks[name]['port']

        if networks[name]['ssl']:
            reactor.connectSSL(host, port, factory, ssl.ClientContextFactory())
        else:
            reactor.connectTCP(host, port, factory)

    reactor.run()

