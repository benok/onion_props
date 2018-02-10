class Test:
    def __init__(self, val):
        self.others = {}
        self.val = val

    def __setattr__(self, name, val):
        self.others[str(name)] = val
    
    def __getattr__(self, name=None):
        if name is None:
            return self.val
        else:
            return {}

t = Test(123)
print(t)
print(t.asdf)