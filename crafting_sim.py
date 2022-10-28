from enum import auto, Enum
import random

REQUIRED_PROGRESS = 7480
REQUIRED_QUALITY = 13620
STARTING_DURABILITY = 60

CRAFTSMANSHIP = 3803
CONTROL = 3592
CP = 691

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
    waste_not = auto()
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
    focuesd_synthesis = auto()
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

class Crafting_State:
    ############    States for actions (buffs/combos)       ############

    # combo states
    touch_combo = 0 # 0: no combo, 1: after basic touch, 2: after standard touch
    observe = 0 # combo for focused synth/touch
    
    # steps left on each buff
    waste_not_1 = 0
    waste_not_2 = 0
    manipulation = 0
    great_strides = 0
    veneration = 0
    innovation = 0
    final_appraisal = 0

    # uses left on specialist actions
    careful_observation = 3
    heart_and_soul = 1

    # state for starting actions (reflect/muscle memory)
    initial = True

    ############     States for Craft (progress/condition)     ############
    progress = 0
    quality = 0
    condition = Condition.normal
    durability = STARTING_DURABILITY

    def crafting_sim(self, action: Action) -> int:  # returns reward
        if (action == Action.careful_observation):
            self.condition = Condition.RANDOM()
            return 0

        

        self.__decrement_buffs()


    def __decrement_buffs(self):
        if (self.waste_not_1 > 0):
            self.waste_not_1 -= 1
        if (self.waste_not_2 > 0):
            self.waste_not_2 -= 1
        if (self.manipulation > 0):
            self.manipulation -= 1
        if (self.great_strides > 0):
            self.great_strides -= 1
        if (self.veneration > 0):
            self.veneration -= 1
        if (self.innovation > 0):
            self.innovation -= 1
        if (self.final_appraisal > 0):
            self.final_appraisal -= 1