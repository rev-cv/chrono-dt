class ChronoOperators(object):
    def __init__(self):
        super(ChronoOperators, self).__init__()
    
    def __lt__(self, other):
        #x < y
        if self.getUnixEpoch() < other.getUnixEpoch():
            return True
        else: return False 

    def __le__(self, other):
        #x <= y
        if self.getUnixEpoch() <= other.getUnixEpoch():
            return True
        else: return False

    def __eq__(self, other):
        #x == y
        if self.getUnixEpoch() == other.getUnixEpoch():
            return True
        else: return False

    def __ne__(self, other):
        #x != y
        if self.getUnixEpoch() != other.getUnixEpoch():
            return True
        else: return False

    def __gt__(self, other):
        #x > y
        if self.getUnixEpoch() > other.getUnixEpoch():
            return True
        else: return False

    def __ge__(self, other):
        #x >= y
        if self.getUnixEpoch() >= other.getUnixEpoch():
            return True
        else: return False
        