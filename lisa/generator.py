# coding: utf-8
"""
Lisabot 2.4.0 chatter (Lisabot 3 ported) 
"""
from __future__ import unicode_literals

import itertools
import random
import string
from functools import partial
from operator import lt, itemgetter
from itertools import imap, ifilter, islice, izip
from curtana.lib.prelude import compose, star

from lisabot2.core.chatter.util import *

# coding: utf-8

from collections import defaultdict, Counter
from operator import itemgetter
from itertools import chain, repeat, product
import random

class Table:
    def __init__(self):
        self.table = defaultdict(Counter)
    def __getitem__(self, key):
        return self.table[key]
    def drop(self, n=1):
        for _ in xrange(n):
            key = random.choice(self.table.keys())
            self.table[key] -= 1
            if self.table[key] == 0:
                del self.table[key]
    
    def update(self, iterable):
        buf = [None] * 3
        n = 0
        for i in chain(iterable, [None] * 2):
            buf.pop(0)
            buf.append(i)
            self.table[buf[0], buf[1]][buf[2]] += 1
            n += 1
        return n

def removed(x, xs):
    xs_ = list(xs)
    xs_.remove(x)
    return xs_

def update_association(table, source, target):
    table.update(product(source, target))
    
def generate(table,
             association=None, sentence=None,
             N=16, P=200, first=20, extra=5,
             f=lambda value, bias:value / 10 * bias):
    
    if association:
        bias = lambda word: sum(association[w, word] for w in sentence)
    else:
        bias = lambda x: 0
    
    stack = [([None, x], f(v, bias(x))) for x, v in table[None, None].most_common(first)]
    
    result = []
    while stack:
        seq, score = stack.pop(0)
        
        if seq[-1] == None:
            result.append((seq, score))
            if len(result) > N:
                return result
            continue
        
        target = table[seq[-2], seq[-1]]

        for word, v in target.most_common(extra):
            stack.append((seq + [word], f(v, bias(x))))

        stack.sort(key=itemgetter(1))
        stack = stack[:P]
    return result

def load():
    import MeCab
    def wakati(text):
        return MeCab.Tagger(str("-Owakati")).parse(text).decode("utf-8").strip(" \n").split(" ")

    table = Table()
    for line in open("corpus.txt"):
        table.update(wakati(line.strip(str("\r\n"))))
    return table

def format_words(wordlist, conversation=False):
    """単語のリストから文章を作る。"""
    flag = False
    result = ""
    for word in wordlist:
        if isterminal(word):
            continue
        if word[0] == "#":
            result += " "
        if conversation and word == "リサ":
            result += "%(name)s"
            continue
        if word in ["俺", "僕", "私", "わし", "あたい", "あたし", "わたし"]:
            result += "自分"
            continue

        if conversation and word in ["お前", "きみ", "あなた", "貴方", "てめえ", "あんた", "貴様"]:
            result += "%(name)s氏"
            continue
        newflag = all(x in string.ascii_letters for x in word)
        result += " " * (flag and newflag) + word
        flag = newflag
    return result
