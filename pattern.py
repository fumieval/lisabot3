# coding: utf-8
from __future__ import unicode_literals
from curtana.lib.parser import Parser
from curtana.lib.container import TupleA
from curtana.lib.parser_aliases import C, S, P, R, T, RE

import itertools as I

DELIMITER = +(reduce(Parser.__or__, I.imap(C, [" ", "　", ",", ".", "、", "。"])))

DECIMAL = int ** +P(unicode.isdigit)
HEXADECIMAL = S("0x") >> int ** +P("0123456789abcdef０１２３４５６７８９".__contains__) * R(16)
BINARY = S("0") >> int ** +(C("0") | C("1") | C("０" | C("１"))) * R(2)

JPN_NUM_EXPR = ((C("零") | C("〇") | C("ぜ") >> -C("ー") >> C("ろ") | C("れ") >> -C("ー") >> C("い")) >> R(0)
                | (C("一") | C("壱") | C("い") >> -C("ー") >> C("ち")) >> R(1)
                | (C("二") | C("弐") | C("に") >> -C("ー") >> C("い").opt) >> R(2)
                | (C("三") | C("参") | C("さ") >> -C("ー") >> C("ん")) >> R(3)
                | (C("四") | C("よ") >> -C("ー") >> C("ん")) >> R(4)
                | (C("五") | C("ご") >> -C("ー") >> (C("お") | C("う")).opt) >> R(5)
                | (C("六") | C("ろ") >> -C("ー") >> C("く")) >> R(6)
                | (C("七") | C("な") >> -C("ー") >> C("な") | C("し") >> -C("ー") >> C("ち")) >> R(7)
                | (C("八") | C("は") >> -C("ー") >> C("ち")) >> R(8)                
                | (C("九") | S("きゅ") >> -C("ー") >> C("う").opt | C("く")) >> R(9))

SEQ_PARSER = T(+((DECIMAL | HEXADECIMAL | BINARY | JPN_NUM_EXPR) << DELIMITER.opt))

