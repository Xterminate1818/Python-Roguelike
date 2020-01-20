import weakref as wr


class Test:
    active = set()

    def __init__(self):
        self.active.add(wr.ref(self))


t = Test()
print(Test.active)
