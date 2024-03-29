# coding: utf-8
from __future__ import unicode_literals

from curtana.lib.prelude import star, compose, fanout
from curtana.lib.monadIO import *
from curtana.lib.stream import Map, BufferBy
from curtana.common.twitterlib import ApiMod

import cPickle
import re
import datetime
import operator as OP
import random

from itertools import imap
from functools import partial
from collections import Counter

import lisabot3.lisa.generator as G
import lisabot3.responder as B
from lisabot3.lisa import vocab

GROUPER = BufferBy(compose(partial(OP.lt, 140 - 6), compose(sum, Map(len))))

ENTITIES = re.compile("[QR]T @\w+.*|\.(@\w+ )+|http:\/\/(\w+|\.|\/)*|@\w+")

class ResponderLisa(B.Base, B.Storable, vocab.Vocabulary):
    store_attributes = ["impression", "talked", "markov_table", "assoc_table"]
    def __init__(self, name):
        from curtana.lib.parser_aliases import RE, R
        B.Base.__init__(self, ApiMod.from_name(name))
        vocab.Vocabulary.__init__(self)
        
        self.screen_name = name
        self.talked = []
        self.assoc_table = Counter()
        self.markov_table = G.Table()
        self.load(B.PATH)

        self.pattern = (RE("もしゃもしゃ|モシャモシャ|もふもふ|モフモフ") >> R(self.response0)
                        | RE("(^|む|[^く])ぎゅ[っうぅー]?") >> R(self.response1)
                        | RE("なでなで|ナデナデ") >> R(self.response2)
                        | RE("ぺろぺろ|ペロペロ|ちゅっちゅ｜チュッチュ") >> R(self.response3) 
                        )
        self.voluntary = (RE("((^|[^ァ-ヾ])リサ|(^|[^ぁ-ゞ])りさ)(ちゃん|チャン)")
                         >> R(compose(star(OP.rshift), fanout(self.chan_ha_fuyou, self.favorite)))
                         #|RE("((^|[^ァ-ヾ])リサ|^りさ)") >> R(self.favorite)
                         )
    
    def learn(self, sentence, in_reply_to_status_id):
        self.markov_table.update(sentence)
        if in_reply_to_status_id:
            G.update_association(self.assoc_table,
                G.wakati(ENTITIES.sub("", self.api.showStatus(id=in_reply_to_status_id)["text"])),
                sentence)
    
    @joinIO
    def for_mizutani(self, status):
        
        if status["user"]["screen_name"] != "mizutani_j_bot":
            return Return(IOZero)
            
        if "下校時間です" in status["text"]:
            if self.talked:
                mentions = GROUPER("@" + x + " " for x in self.talked)
                return sequence(self.post(".{0} 《下校》".format("".join(mention))) for mention in mentions)
                self.talked = []
            else:
                return self.post("帰る")
        else:
            return self.favorite(status)

    @joinIO
    def for_everyone(self, status):
        text_lower = status["text"].lower()
        text = ENTITIES.sub("", status["text"])
        sentence = G.wakati(text)
        self.learn(sentence, status["in_reply_to_status_id"])
        level = 0
        if status["in_reply_to_screen_name"] == None:
            level += 1
        elif status["in_reply_to_screen_name"] == self.screen_name:
            level += 2

        if re.search("@" + self.screen_name.lower() + "[^\w_]", text_lower):
            level += 2
        
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
                
                return self.reply(status, G.format_words(random.choice(G.generate(self.markov_table, self.assoc_table, sentence, N=8, P=50, first=0.5, extra=6))[0], conversation=True).format(name=status["user"]["name"]))
                
        return Return(IOZero)

    def issleeping(self):
        return False
    
    def action(self, status):
        return (B.Base.action(self, status)
                | Satisfy(self.issleeping)
                | self.for_mizutani(status)
                | self.for_everyone(status)
                | Return(IOOne))