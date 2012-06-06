# coding: utf-8
import itertools
from itertools import chain, islice
import random
from collections import defaultdict, Counter
from operator import itemgetter

class TriadTable:
    def __init__(self):
        self.left_1 = defaultdict(Counter)
        self.right_1 = defaultdict(Counter)
        self.left_2 = defaultdict(Counter)
        self.right_2 = defaultdict(Counter)
        
    def add(self, (left, center, right)):
        self.left_1[center][left] += 1
        self.right_1[center][right] += 1
        self.left_2[center, right][left] += 1
        self.right_2[left, center][right] += 1
    
    def update(self, iterable):
        buf = [None] * 3
        for i in itertools.chain(iterable, [None] * 2):
            buf.pop(0)
            buf.append(i)
            self.add(buf)

def load():
    import MeCab
    def wakati(text):
        return MeCab.Tagger(str("-Owakati")).parse(text).decode("utf-8").strip("\n").split(" ")

    table = TriadTable()
    for line in open("corpus.txt"):
        table.update(wakati(line.strip("\r\n")))
    return table
