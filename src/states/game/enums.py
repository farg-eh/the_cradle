from enum import IntEnum, nonmember, auto


class Items(IntEnum):
    # animal foods
    CHICKEN = 0
    # seafoods
    SMALL_FISH = 1
    MID_FISH = 2
    BIG_FISH = 3
    # sea trash
    BOOT = 4
    SEAWEED = 5
    # seeds
    TOMATO_SEED = 6
    WHEAT_SEED = 7
    # corps
    TOMATO = 8
    WHEAT = 9
    # clothes
    SHIRT = 10
    # WEAPONS
    SWORD = 11
    BOW = 12
    ARROW = 13
    COIN = 14

    # non memebrs ~~~~~~~
    # x4 x2
    _PRICES = nonmember([
        80,  # chicken
        16,  # small fish
        48,  # mid fish
        96,  # big fish
        4,   # boot 
        2,   # seaweed 
        8,   # tomato seed 
        12,  # wheat seed
        10,  # tomato 
        6,   # wheat 
        80,  # shirt  
        400, # sword 
        600, # bow 
        16, # arrow
        1 # coin
        ])

    def get_price(self):
        return self._PRICES[self]

    def get_str(self):
        return self.name.lower()



