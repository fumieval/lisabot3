from curtana.common import userstream
from curtana.common.twitterlib import ApiMod
from lisabot3.lisa.response import ResponderLisa
import threading

REGISTERD_NAME = "Lisa_math"

class Execute(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action
        self.daemon = True
    def run(self):
        self.action.do()

def consume(name, responder):
    for status in userstream.iterstream(userstream.streamopen(name)):
        Execute(responder.action(status)).start()

def main(name):
    consume(name, ResponderLisa(name))

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "run":
        main(sys.argv[2])
    elif sys.argv[1] == "post":
        ApiMod.from_name(REGISTERD_NAME).updateStatus(status=sys.argv[2])
    elif sys.argv[1] == "tweet":
        pass #G.format_words(G.generate(table, N=32, P=100, extra=3)[16][0])