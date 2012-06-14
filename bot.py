from curtana.common import streaming
from curtana.common.twitterlib import ApiMod
from lisabot3.lisa.response import ResponderLisa
from lisabot3.lisa import vocab
import threading

REGISTERD_NAME = "Lisa_math"

class Execute(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action
        self.daemon = True
    def run(self):
        self.action.do()

class TrackFollowme(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = name
        self.api = ApiMod.from_name(name)
    def run(self):
        stream = streaming.streamopen(self.name, streaming.STATUSES_FILTER_URL, track="#Lisa_math_follow_me")
        for status in stream:
            self.api.createFriendship(user_id=status["user"]["id_str"])
            self.api.updateStatus(vocab.FOLLOW_COMPLETE.format(status["user"]["screen_name"]), in_reply_to_status_id=status["id_str"])

def consume(name, responder):
    for status in streaming.iterstream(streaming.streamopen(name)):
        Execute(responder.action(status)).start()

def main(name):
    TrackFollowme(name).start()
    consume(name, ResponderLisa(name))

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "run":
        main(REGISTERD_NAME)
    elif sys.argv[1] == "post":
        ApiMod.from_name(REGISTERD_NAME).updateStatus(status=sys.argv[2])
    elif sys.argv[1] == "tweet":
        pass #G.format_words(G.generate(table, N=32, P=100, extra=3)[16][0])