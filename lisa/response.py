# coding: utf-8
from __future__ import unicode_literals

from curtana.lib.monadIO import *
from curtana.lib.stream import bufferBy
from curtana.common.twitterlib import ApiMod
from lisabot3.base import ResponderBase
from lisabot3.lisa.vocab import ResponderVocab

import re
import datetime
import operator
from itertools import imap
from functools import partial

ENTITIES = re.compile("[QR]T @\w+.*|\.(@\w+ )+|http:\/\/(\w+|\.|\/)*|@\w+")

def compose(f, g):
    return lambda x: f(g(x))

c = compose
j = lambda f: lambda x, y: lambda z: f(x(z), y(z))

class ResponderLisa(ResponderBase, ResponderVocab):
    
    def __init__(self, name):
        from curtana.lib.parser_aliases import RE, R
        ResponderBase.__init__(self, ApiMod.from_name(name))
        ResponderVocab.__init__(self)
        self.screen_name = name
        self.talked = []
        self.pattern = (RE("もしゃもしゃ|モシャモシャ|もふもふ|モフモフ") >> R(self.response0)
                        | RE("(^|む|[^く])ぎゅ[っうぅー]?") >> R(self.response1)
                        | RE("なでなで|ナデナデ") >> R(self.response2)
                        | RE("ぺろぺろ|ペロペロ|ちゅっちゅ｜チュッチュ") >> R(self.response3) 
                        | R(self.response5)
                        )
        self.voluntary = RE("((^|[^ァ-ヾ])リサ|(^|[^ぁ-ゞ])りさ)(ちゃん|チャン)") >> R(self.response4 self.favorite)
        
    @joinIO
    def for_mizutani(self, status):
        
        if status["user"]["screen_name"] == "mizutani_j_bot":
            if "下校時間です" in status["text"]:
                if self.talked:
                    mentions = bufferBy(c(partial(operator.lt, 140 - 6),
                                          c(sum, partial(imap, len)))
                                        , ("@" + x + " " for x in self.talked))
                    return sequence(self.post(".{0} 《下校》".format("".join(mention))) for mention in mentions)
                else:
                    return self.post("帰る")
            else:
                return self.favorite(status)
        
        return Return(IOZero)

    @joinIO
    def for_everyone(self, status):
        text_lower = status["text"].lower()
        level = 0
        if status["in_reply_to_screen_name"] == None:
            level += 1
        elif status["in_reply_to_screen_name"] == self.screen_name:
            level += 2
        if re.search("@" + self.screen_name.lower() + "[^\w_]", text_lower):
            level += 2
        
        text = ENTITIES.sub("", status["text"])
        
        if level >= 1:
            res = self.voluntary(text)(status)
            if res:
                return res
            if level >= 2:
                self.talked.append(status["user"]["screen_name"])
                if level >= 4:
                    return self.pattern(text)(status)
        
        return Return(IOZero)

    def issleeping(self):
        return False
    
    def action(self, status):
        return (ResponderBase.action(self, status)
                | Satisfy(self.issleeping)
                | self.for_mizutani(status)
                | self.for_everyone(status)
                | Return(IOOne))
        