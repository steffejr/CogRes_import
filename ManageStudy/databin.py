class databin(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
