from types import SimpleNamespace


class Message(SimpleNamespace):
    def dict(self):
        return self.__dict__
