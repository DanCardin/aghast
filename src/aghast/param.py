import functools
import operator


class Param:
    def __init__(self, actions=None):
        if actions is None:
            actions = []
        self.actions = actions

    def __gt__(self, other):
        action = functools.partial(operator.__ge__, other)
        return type(self)(self.actions + [action])

    def __eq__(self, other):
        action = functools.partial(operator.__eq__, other)
        return type(self)(self.actions + [action])

    def __truediv__(self, other):
        action = functools.partial(operator.__truediv__, b=other)
        return type(self)(self.actions + [action])

    def __rtruediv__(self, other):
        action = functools.partial(operator.__truediv__, a=other)
        return type(self)(self.actions + [action])


x = Param()
