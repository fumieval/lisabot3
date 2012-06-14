# coding: utf-8
from __future__ import unicode_literals
from collections import defaultdict
from functools import partial
import random
FOLLOW_COMPLETE = "@{0} フォロー完了"
class Vocabulary:
    def __init__(self):
        self.impression = defaultdict(int)
    def choice(self, status, pattern, els):
        """choices response by the impression."""
        for t, xs in pattern:
            if t < self.impression[status["user"]["screen_name"]]:
                return random.choice(xs)
        return random.choice(els).format(name=status["user"]["name"])
    
    def response0(self, status):
        r = partial(self.reply, status)
        return r(self.choice(status,
                             [(15, ["きゃうん！", "きゃうん…", "きゃん！", "……コンティニュー//", "……つづけて//", "やめて…",]),
                              (4, ["きゃうん！","きゃうん…","きゃうん…","きゃん！","やめて","だめ","やめて、{name}氏"])],
                              ["やめて、{name}氏","{name}氏、やめて","やめて…","だめ","やめて"]))
    
    def response1(self, status):
        r = partial(self.reply, status)
        return r(self.choice(status,
                             [(20, ["きゃうん！","きゃうっ！","きゃん！","やめて、{name}氏","{name}氏、やめて"])],
                             ["やめて、{name}氏","{name}氏、やめて","やめて…","だめ","やめて"]))   
    
    def response2(self, status):
        r = partial(self.reply, status)
        return r(self.choice(status,
                             [(3, ["……", "つづけて"])],
                             ["邪魔しないで", "不要"]))
    
    def response3(self, status):
        r = partial(self.reply, status)
        return r(self.choice([(6, ["きゃうん！", "きゃうん…", "きゃん！", "やめて、{name}氏", "{name}氏、やめて"])],
                            ["やめて、{name}氏","{name}氏、やめて","やめて…","やめて"]))

    def chan_ha_fuyou(self, status):
        return self.reply(status, "《ちゃん》は不要")

    def response5(self, status):
        return self.reply(status, random.choice("……"))
    
    def responseauto(self, status):
        pass
    