from crafting_types import Action
from enum import Enum

REQUIRED_PROGRESS = 7480
REQUIRED_QUALITY = 13500 # changed 13620 to 13500 as the last 120 doesnt matter
STARTING_DURABILITY = 60

RECIPE_LEVEL_PROG_DIV = 180
RECIPE_LEVEL_PROG_MOD = 100
RECIPE_LEVEL_QUAL_DIV = 180
RECIPE_LEVEL_QUAL_MOD = 100

CRAFTSMANSHIP = 3803
CONTROL = 3592
INITIAL_CP = 691

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

GOOD_MULTIPLIER = 1.5
MALLEABLE_MULTIPLIER = 1.5
PRIMED_ADDITIONAL_TURNS = 2

TOUCH_COMBO_CP = 18
MASTERS_MEND_DURABILITY = 30
MANIPULATION_DURABILITY = 5

POTENCIES = [0 for i in range(len(Action) + 1)] # add extra index due to 1 indexing
POTENCIES[Action.basic_synthesis.value] = 120
POTENCIES[Action.basic_touch.value] = 100
POTENCIES[Action.hasty_touch.value] = 100
POTENCIES[Action.rapid_synthesis.value] = 500
POTENCIES[Action.standard_touch.value] = 125
POTENCIES[Action.byregots_blessing.value] = 100
POTENCIES[Action.precise_touch.value] = 150
POTENCIES[Action.muscle_memory.value] = 300
POTENCIES[Action.careful_synthesis.value] = 180
POTENCIES[Action.prudent_touch.value] = 100
POTENCIES[Action.focused_synthesis.value] = 200
POTENCIES[Action.focused_touch.value] = 150
POTENCIES[Action.reflect.value] = 100
POTENCIES[Action.prepatory_touch.value] = 200
POTENCIES[Action.groundwork.value] = 360
POTENCIES[Action.delicate_synthesis.value] = 100
POTENCIES[Action.intensive_synthesis.value] = 400
POTENCIES[Action.advanced_touch.value] = 150
POTENCIES[Action.prudent_synthesis.value] = 180
POTENCIES[Action.trained_finesse.value] = 100

SUCCESS = [0 for i in range(len(Action) + 1)] # add extra index due to 1 indexing
SUCCESS[Action.focused_synthesis.value] = 0.5
SUCCESS[Action.focused_touch.value] = 0.5
SUCCESS[Action.rapid_synthesis.value] = 0.5
SUCCESS[Action.hasty_touch.value] = 0.6

CP_COST = [0 for i in range(len(Action) + 1)] # add extra index due to 1 indexing
CP_COST[Action.basic_synthesis.value] = 0
CP_COST[Action.basic_touch.value] = 18
CP_COST[Action.masters_mend.value] = 88
CP_COST[Action.hasty_touch.value] = 0
CP_COST[Action.rapid_synthesis.value] = 0
CP_COST[Action.observe.value] = 7
CP_COST[Action.tricks_of_the_trade.value] = -20
CP_COST[Action.waste_not_1.value] = 56
CP_COST[Action.veneration.value] = 18
CP_COST[Action.standard_touch.value] = 32
CP_COST[Action.great_strides.value] = 32
CP_COST[Action.innovation.value] = 18
CP_COST[Action.final_appraisal.value] = 1
CP_COST[Action.waste_not_2.value] = 98
CP_COST[Action.byregots_blessing.value] = 24
CP_COST[Action.precise_touch.value] = 18
CP_COST[Action.muscle_memory.value] = 6
CP_COST[Action.careful_synthesis.value] = 7
CP_COST[Action.manipulation.value] = 96
CP_COST[Action.prudent_touch.value] = 25
CP_COST[Action.focused_synthesis.value] = 5
CP_COST[Action.focused_touch.value] = 18
CP_COST[Action.reflect.value] = 6
CP_COST[Action.prepatory_touch.value] = 40
CP_COST[Action.groundwork.value] = 18
CP_COST[Action.delicate_synthesis.value] = 32
CP_COST[Action.intensive_synthesis.value] = 6
CP_COST[Action.advanced_touch.value] = 46
CP_COST[Action.prudent_synthesis.value] = 18
CP_COST[Action.trained_finesse.value] = 32
CP_COST[Action.careful_observation.value] = 0
CP_COST[Action.heart_and_soul.value] = 0

class ACTION_TYPE(set, Enum):
    PROGRESS = {Action.basic_synthesis, Action.rapid_synthesis, Action.muscle_memory, Action.careful_synthesis, Action.focused_synthesis, Action.groundwork, Action.delicate_synthesis, Action.intensive_synthesis, Action.prudent_synthesis}
    QUALITY = {Action.basic_touch, Action.hasty_touch, Action.standard_touch, Action.byregots_blessing, Action.precise_touch, Action.prudent_touch, Action.focused_touch, Action.reflect, Action.prepatory_touch, Action.delicate_synthesis, Action.advanced_touch, Action.trained_finesse}
    NO_TURN = {Action.heart_and_soul, Action.final_appraisal, Action.careful_observation}
    DOUBLE_DURABILITY = {Action.prepatory_touch, Action.groundwork}
    HALF_DURABILITY = {Action.prudent_synthesis, Action.prudent_touch}
    CHANCE_OF_FAIL = {Action.focused_synthesis, Action.focused_touch, Action.rapid_synthesis, Action. hasty_touch}
    OBSERVE_ACTIONS = {Action.focused_synthesis, Action.focused_touch}
    GOOD_ACTIONS = {Action.tricks_of_the_trade, Action.intensive_synthesis, Action.precise_touch}
    INITIAL_ACTIONS = {Action.muscle_memory, Action.reflect}
    EXTRA_INNER_QUIET = {Action.reflect, Action.prepatory_touch, Action.precise_touch}
    BUFF_ACTIONS = {Action.observe, Action.tricks_of_the_trade, Action.waste_not_1, Action.veneration, Action.great_strides, Action.innovation, Action.waste_not_2, Action.manipulation, Action.trained_finesse}