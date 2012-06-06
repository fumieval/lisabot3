from __future__ import unicode_literals
from curtana.lib.monadIO import *

import datetime

class ResponderBase:

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
        return self.api.createFavorite(id=status["id"])

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
               | self.ping(status)
               | Satisfy(lambda: self.is_limit_exceeded(status)))