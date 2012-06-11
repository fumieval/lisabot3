import sys
import re
from collections import defaultdict
from itertools import ifilter
from curtana.common import twitterlib

ENTITIES = re.compile("RT @\w+.*|\.(@\w+ )+|http:\/\/(\w+|\.|\/)*|@\w+|\n")

if __name__ == "__main__":
    with open("talk.txt", "a") as f:
        api = twitterlib.ApiMod.from_name("Risa_math")
        tweets = []
        for page in xrange(int(sys.argv[1]), int(sys.argv[2]) + 1):
            print "Page %d:" % page,
            for status in api.getHomeTimeline(page=page):
                tweets.append((status["id"], status["text"], status["in_reply_to_status_id"]))
            print "Done."
        texts = {}
        table = defaultdict(list)
        for i, text, to in tweets:
            texts[i] = text
            if to in texts:
                table[to].append(text)
        for i in table:
            print >> f, texts[i]
            for text in table[i]:
                print >> f, "\t" + text 
        