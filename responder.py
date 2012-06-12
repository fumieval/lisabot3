from __future__ import unicode_literals
from curtana.lib.monadIO import *
import shelve
import datetime
from itertools import ifilter, imap

PATH = "/home/fumiaki/Dropbox/Python/lisabot3/var/lisabot3.shelf"

class Storable():
    def load(self, path):
        data = shelve.open(path, protocol=1)
        for key in ifilter(data.__contains__, imap(str, self.__class__.store_attributes)):
            self.__dict__[key] = data[key]
    
    def save(self, path):
        data = shelve.open(path, protocol=1)
        for key in self.__class__.store_attributes:
            data[str(key)] = self.__dict__[key]

class Base(object):

    def __init__(self, api):
        self.api = api

    @wrapIO
    def reply(self, status, text):
        return self.api.updateStatus(status="@{0} {1}".format(status["user"]["screen_name"], text),
                                     in_reply_to_status_id=unicode(status["id"]))
    @wrapIO
    def post(self, text):
        return self.api.updateStatus(status=text)
        
    @wrapIO
    def favorite(self, status):
        return self.api.createFavorite(id=unicode(status["id"]))
    
    @joinIO
    def command(self, status):
        if "#ctrl" in status["text"] and status["user"]["screen_name"] == "fumieval":
            
            line = status["text"][status["text"].find(u"$$") + 2:]
            cmd = line.split()
            if cmd[0] == "dump":
                #FIXME Base doesn't provide saving
                self.save(PATH)
                print "{0} Dumped to {1}".format(datetime.datetime.today().strftime("%D %H:%M:%S"), PATH)
                return Return(IOOne)
        
        return Return(IOZero)
    
    @joinIO
    def ping(self, status):
        if "#ping" in status["text"]:
            now = datetime.datetime.today().strftime("%a %b %d %H:%M:%S +0000 %Y")
            return self.reply(status, "#pong {0} (#ping {1})".format(now, status["created_at"]))
        
        return Return(IOZero)
        
    def isnotStatus(self, status):
        return not ("user" in status and "text" in status)
        
    def isignorable(self, status):
        return (status["user"]["screen_name"] == self.screen_name or
                "retweeted_status" in status)
    
    def is_limit_exceeded(self, status):
        return False

    def action(self, status):
        return ( Satisfy(lambda: self.isnotStatus(status))
               | Satisfy(lambda: self.isignorable(status))
               | self.command(status)
               | self.ping(status)
               | Satisfy(lambda: self.is_limit_exceeded(status)))