#! /usr/bin/python

import random

class Randomizer(object):
    def __init__(self):
        random.seed()

class Dice(Randomizer):
    def __init__(self, min = 1, max = 6):
        self._min = min
        self._max = max
        self = super(Dice, self).__init__()

    def roll(self):
        return random.randint(self._min, self._max)

class D16(Dice):
    def __init__(self):
        self = super(D16, self).__init__(1, 16)

class D20(Dice):
    def __init__(self):
        self = super(D20, self).__init__(1, 20)

class D100(Dice):
    def __init(self):
        self = super(D100, self).__init__(1, 100)
