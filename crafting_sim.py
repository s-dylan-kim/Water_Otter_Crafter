from constants import POTENCIES, CP_COST, SUCCESS, ACTION_TYPE
from types import Condition, Action

REQUIRED_PROGRESS = 7480
REQUIRED_QUALITY = 13620
STARTING_DURABILITY = 60

CRAFTSMANSHIP = 3803
CONTROL = 3592
CP = 691


CAREFUL_OBSERVATION_USES = 3
HEART_AND_SOUL_USES = 1

FINAL_APPRAISAL_LENGTH = 5
WASTE_NOT_1_LENGTH = 4
WASTE_NOT_2_LENGTH = 8
MANIPULATION_LENGTH = 8
GREAT_STRIDES_LENGTH = 3
VENERATION_LENGTH = 4
INNOVATION_LENGTH = 4
MUSCLE_MEMORY_LENGTH = 5

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
    careful_observation = CAREFUL_OBSERVATION_USES
    heart_and_soul = HEART_AND_SOUL_USES

    # state for starting actions (reflect/muscle memory)
    initial = True

    ############     States for Craft (progress/condition)     ############
    progress = 0
    quality = 0
    condition = Condition.normal
    durability = STARTING_DURABILITY

    def crafting_sim(self, action: Action) -> tuple[int, bool]:  # returns (reward, done?)

        # check either of actions that dont progress turns
        if (action in ACTION_TYPE.NO_TURN):
            if (action == Action.final_appraisal):
                self.final_appraisal = FINAL_APPRAISAL_LENGTH
            return (0, False)

        if (action in ACTION_TYPE.PROGRESS):
            pass
        if (action in ACTION_TYPE.QUALITY):
            pass

        # change condition and decrement buffs
        self.condition = Condition.RANDOM()
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