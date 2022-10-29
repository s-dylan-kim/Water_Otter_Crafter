from enum import auto, Enum
import random

class Condition(Enum):
    normal = auto()
    good = auto() # 1.5x quality gain (also allows using good actions)
    malleable = auto() # 1.5x progress gain
    centered = auto() # improves success rate by 25%
    primed = auto() # next action lasts 2 more steps
    sturdy = auto() # next action uses half durability

    @classmethod
    def RANDOM(cls):
        return random.choice(list(cls.__members__.values()))


class Action(Enum):
    basic_synthesis = auto()
    basic_touch = auto()
    masters_mend = auto()
    hasty_touch = auto()
    rapid_synthesis = auto()
    observe = auto()
    tricks_of_the_trade = auto()
    waste_not_1 = auto()
    veneration = auto()
    standard_touch = auto()
    great_strides = auto()
    innovation = auto()
    final_appraisal = auto()
    waste_not_2 = auto()
    byregots_blessing = auto()
    precise_touch = auto()
    muscle_memory = auto()
    careful_synthesis = auto()
    manipulation = auto()
    prudent_touch = auto()
    focused_synthesis = auto()
    focused_touch = auto()
    reflect = auto()
    prepatory_touch = auto()
    groundwork = auto()
    delicate_synthesis = auto()
    intensive_synthesis = auto()
    advanced_touch = auto()
    prudent_synthesis = auto()
    trained_finesse = auto()
    careful_observation = auto()
    heart_and_soul = auto()