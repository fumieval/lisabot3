
class Association:
    def __init__(self):
        self.table = {}
    def train(self, source, target):
        n = len(target)
        for dom in source:
            for cod in target:
                self.table[dom][cod] = (self.table[dom][cod] + 1) / 2