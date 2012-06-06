import itertools
import random
from collections import defaultdict, Counter
def compose(f, g):
    return lambda x: f(g(x))

def choice(value, iterable):
    v = value
    for i, el in iterable:
        if el >= v:
            return i
        else:
            v -= el

def choice_forward(table, origin, keywords=[]):
    nexts = table[origin].most_common()
    if nexts:
        s = 0
        for i, el in nexts:
            if i in keywords:
                keywords.remove(i)
                return i
            s += el
        else:
            return choice(random.randint(0, s), nexts)

def generate_forward(table, origin, keywords=[]):
    word = choice_forward(table, origin, keywords)
    if word and word != END:
        yield word
        for i in generate_forward(table, origin[1:] + (word,), keywords):
            yield i

def consume(x, xs):
    result = []
    for i in xs:
        if i == x:
            for j in xs:
                result.append(el)
            break
        else:
            result.append(el)

def generate_greedy(table, origin, keywords=[]):
    word = choice_forward(table, origin, keywords)
    nexts = table[origin].most_common()
    targets = [generate_greedy(table, word,
                              consume(keywords, x)) for word, _ in nexts]

    #for target in targets:
    
    # yield v, word vという実数で自己主張し、wordで次の単語を返す
    # yield   
def update_table(table, step, iterable):
    dom = (BEGIN,) * step
    for i in itertools.chain(iterable, [END]):
        table[dom][i] += 1
        dom = dom[1:] + (i,)
        
class MarkovGenerator:
    
    def __init__(self, step=2):
        self.table = defaultdict(Counter)
        self.table_op = defaultdict(Counter)
        self.table_pre = defaultdict(Counter)
        self.step = step
    
    def update(self, words):
        update_table(self.table, self.step, words)
        update_table(self.table_op, self.step, reversed(words))
        for d, c in self.table:
            self.table_pre[d][c] += 1
        
    def generate(self, keywords=[]):
        return list(generate_forward(self.table, (BEGIN,) * self.step, list(keywords)))
    
    def generateby(self, key):
        pass
    
    def generate_beginwith(self, origin, keywords=[]):
        keywords_ = list(keywords)
        
        origin_ = (origin, choice_forward(self.table_pre, origin, keywords))
        
        #generate_forwardが返すイテレータを評価するとkeywords_を消費する点に注意
        left = generate_forward(self.table_op, origin_, keywords_)
        right = generate_forward(self.table, origin_, keywords_)
        
        result = list(origin_)
        
        left_cont, right_cont = True, True
        while left_cont or right_cont: #左→右→左か右→左→右の順で追加するかはいまだ確定せず
            if right_cont:
                try:
                    result.append(next(right))
                except StopIteration:
                    right_cont = False
            if left_cont:
                try:
                    result.insert(0, next(left))
                except StopIteration:
                    left_cont = False
        return result