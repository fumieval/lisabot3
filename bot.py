from curtana.common import userstream
from curtana.common.twitterlib import ApiMod
from lisabot3.lisa.response import ResponderLisa
import threading
import itertools as I
import json

REGISTERD_NAME = "Lisa_math"

class Execute(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action
        self.daemon = True
    def run(self):
        self.action.do()

def consume(name, responder):
    stream = I.imap(json.loads, userstream.iterstream(userstream.streamopen(name)))
    for status in stream:
        Execute(responder.action(status)).start()

def main():
    consume(REGISTERD_NAME, ResponderLisa(REGISTERD_NAME))

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "run":
        main()
    elif sys.argv[1] == "post":
        ApiMod.from_name("Lisa_math").updateStatus(status=sys.argv[2])