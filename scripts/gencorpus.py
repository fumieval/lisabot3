import sys
import re

from itertools import ifilter
from curtana.common import twitterlib

ENTITIES = re.compile("RT @\w+.*|\.(@\w+ )+|http:\/\/(\w+|\.|\/)*|@\w+|\n")

if __name__ == "__main__":
    with open("corpus.txt", "a") as f:
        api = twitterlib.ApiMod.from_name("Risa_math")
        for page in xrange(int(sys.argv[1]), int(sys.argv[2]) + 1):
            print "Page %d:" % page,
            for status in api.getHomeTimeline(page=page):
                s = " ".join(ifilter(None, ENTITIES.sub("", status["text"].encode("utf-8")).split(" ")))
                if s:
                    print >> f, s
            print "Done."