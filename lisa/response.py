# coding: utf-8
from __future__ import unicode_literals

from curtana.lib.prelude import star, compose, fanout
from curtana.lib.monadIO import *
from curtana.lib.stream import Map, BufferBy
from curtana.common.twitterlib import ApiMod
from lisabot3.base import ResponderBase
from lisabot3.lisa.vocab import ResponderVocab

import re
import datetime
import operator as OP
from itertools import imap
from functools import partial

GROUPER = BufferBy(compose(partial(OP.lt, 140 - 6), compose(sum, Map(len))))

ENTITIES = re.compile("[QR]T @\w+.*|\.(@\w+ )+|http:\/\/(\w+|\.|\/)*|@\w+")

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
        self.voluntary = (RE("((^|[^ァ-ヾ])リサ|(^|[^ぁ-ゞ])りさ)(ちゃん|チャン)")
                         #>> R(compose(star(OP.rshift), fanout(self.response4, self.favorite)))
                         >> R(self.response4)
                         |RE("((^|[^ァ-ヾ])リサ|(^|[^ぁ-ゞ])りさ)") >> R(self.favorite))

    @joinIO
    def for_mizutani(self, status):
        
        if status["user"]["screen_name"] != "mizutani_j_bot":
            return Return(IOZero)
            
        if "下校時間です" in status["text"]:
            if self.talked:
                mentions = GROUPER("@" + x + " " for x in self.talked)
                return sequence(self.post(".{0} 《下校》".format("".join(mention))) for mention in mentions)
            else:
                return self.post("帰る")
        else:
            return self.favorite(status)
        

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
            action = self.voluntary(text)
            if action:
                return action(status)
            
            if level >= 2:
                self.talked.append(status["user"]["screen_name"])
                
                if level >= 4:
                    action = self.pattern(text)
                    if action:
                        return action(status)
        
        return Return(IOZero)

    def issleeping(self):
        return False
    
    def action(self, status):
        return (ResponderBase.action(self, status)
                | Satisfy(self.issleeping)
                | self.for_mizutani(status)
                | self.for_everyone(status)
                | Return(IOOne))
        