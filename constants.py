from types import Action
from enum import Enum

POTENCIES = [0 for action in Action]
POTENCIES[Action.basic_synthesis] = 120
POTENCIES[Action.basic_touch] = 100
POTENCIES[Action.hasty_touch] = 100
POTENCIES[Action.rapid_synthesis] = 500
POTENCIES[Action.standard_touch] = 125
POTENCIES[Action.byregots_blessing] = 100
POTENCIES[Action.precise_touch] = 150
POTENCIES[Action.muscle_memory] = 300
POTENCIES[Action.careful_synthesis] = 180
POTENCIES[Action.prudent_touch] = 100
POTENCIES[Action.focused_synthesis] = 200
POTENCIES[Action.focused_touch] = 150
POTENCIES[Action.reflect] = 100
POTENCIES[Action.prepatory_touch] = 200
POTENCIES[Action.groundwork] = 360
POTENCIES[Action.delicate_synthesis] = 100
POTENCIES[Action.intensive_synthesis] = 400
POTENCIES[Action.advanced_touch] = 150
POTENCIES[Action.prudent_synthesis] = 180
POTENCIES[Action.trained_finesse] = 100

SUCCESS = [0 for action in Action]
SUCCESS[Action.focused_synthesis] = 0.5
SUCCESS[Action.focused_touch] = 0.5
SUCCESS[Action.rapid_synthesis] = 0.5
SUCCESS[Action.hasty_touch] = 0.6

CP_COST = [0 for action in Action]
CP_COST[Action.basic_synthesis] = 0
CP_COST[Action.basic_touch] = 18
CP_COST[Action.masters_mend] = 88
CP_COST[Action.hasty_touch] = 0
CP_COST[Action.rapid_synthesis] = 0
CP_COST[Action.observe] = 7
CP_COST[Action.waste_not] = 56
CP_COST[Action.veneration] = 18
CP_COST[Action.standard_touch] = 32
CP_COST[Action.great_strides] = 32
CP_COST[Action.innovation] = 18
CP_COST[Action.final_appraisal] = 1
CP_COST[Action.waste_not_2] = 98
CP_COST[Action.byregots_blessing] = 24
CP_COST[Action.precise_touch] = 18
CP_COST[Action.muscle_memory] = 6
CP_COST[Action.careful_synthesis] = 7
CP_COST[Action.manipulation] = 96
CP_COST[Action.prudent_touch] = 25
CP_COST[Action.focused_synthesis] = 5
CP_COST[Action.focused_touch] = 18
CP_COST[Action.reflect] = 6
CP_COST[Action.prepatory_touch] = 40
CP_COST[Action.groundwork] = 18
CP_COST[Action.delicate_synthesis] = 32
CP_COST[Action.intensive_synthesis] = 6
CP_COST[Action.advanced_touch] = 46
CP_COST[Action.prudent_synthesis] = 18
CP_COST[Action.trained_finesse] = 32
CP_COST[Action.careful_observation] = 0
CP_COST[Action.heart_and_soul] = 0

class ACTION_TYPE(set, Enum):
    PROGRESS = {Action.basic_synthesis, Action.rapid_synthesis, Action.muscle_memory, Action.careful_synthesis, Action.focused_synthesis, Action.groundwork, Action.delicate_synthesis, Action.intensive_synthesis, Action.prudent_synthesis}
    QUALITY = {Action.basic_touch, Action.hasty_touch, Action.standard_touch, Action.byregots_blessing, Action.precise_touch, Action.prudent_touch, Action.focused_touch, Action.reflect, Action.prepatory_touch, Action.delicate_synthesis, Action.advanced_touch, Action.trained_finesse}
    NO_TURN = {Action.heart_and_soul, Action.final_appraisal}
    DOUBLE_DURABILITY = {Action.prepatory_touch, Action.groundwork}
    HALF_DURABILITY = {Action.prudent_synthesis, Action.prudent_touch}
    CHANCE_OF_FAIL = {Action.focused_synthesis, Action.focused_touch, Action.rapid_synthesis, Action. hasty_touch}
    OBSERVE_ACTIONS = {Action.focused_synthesis, Action.focused_touch}
    GOOD_ACTIONS = {Action.tricks_of_the_trade, Action.intensive_synthesis, Action.precise_touch}