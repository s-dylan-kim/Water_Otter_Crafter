from random import Random, randint
from constants import *
from types import Condition, Action
from utils import calc_base_progress, calc_base_quality
import numpy as np

class Crafting_State:
    ############    States for actions (buffs/combos)       ############

    # combo states
    touch_combo = 0 # 0: no combo, 1: after basic touch, 2: after standard touch
    observe = 0 # combo for focused synth/touch
    inner_quiet = 0
    
    # steps left on each buff
    waste_not_1 = 0
    waste_not_2 = 0
    manipulation = 0
    great_strides = 0
    veneration = 0
    innovation = 0
    final_appraisal = 0
    muscle_memory = 0

    # uses left on specialist actions
    careful_observation = CAREFUL_OBSERVATION_USES
    heart_and_soul = HEART_AND_SOUL_USES

    # state for starting actions (reflect/muscle memory)
    initial = True

    ############     States for Craft (progress/condition)     ############
    progress = 0
    quality = 0
    cp = INITIAL_CP
    condition = Condition.normal
    durability = STARTING_DURABILITY

    def crafting_sim(self, action: Action) -> tuple[int, bool]:  # returns (reward, done?)
        # check action validity
        # check first actions
        if (action in ACTION_TYPE.INITIAL_ACTIONS and not self.initial):
            return (-100, False)

        # check good actions
        if (self.condition != Condition.good and action in ACTION_TYPE.GOOD_ACTIONS):
            return (-100, False)
        
        # check half durability actions
        if ((self.waste_not_1 > 0 or self.waste_not_2 > 0) and action in ACTION_TYPE.GOOD_ACTIONS):
            return (-100, False)

        # check CP cost
        cp_cost = CP_COST[action]
        if (action == Action.standard_touch and self.touch_combo == 1 or action == Action.advanced_touch and self.touch_combo == 2):
            cp_cost = TOUCH_COMBO_CP

        if (self.cp < cp_cost):
            return (-100, False)

        # UPDATE CP
        self.cp -= cp_cost

        # check either of actions that dont progress turns
        if (action in ACTION_TYPE.NO_TURN):
            if (action == Action.final_appraisal):
                self.final_appraisal = FINAL_APPRAISAL_LENGTH
            return (0, False)


        # check if actions succeeds
        if (action in ACTION_TYPE.CHANCE_OF_FAIL):
            if (self.observe and action in ACTION_TYPE.OBSERVE_ACTIONS):
                if (SUCCESS[action] < Random.random()):
                    return (0, False)
        
        # track reward
        reward = 0

        if (action in ACTION_TYPE.QUALITY):
            qual = calc_base_quality()
            
            # apply malleable
            if (self.condition == Condition.good):
                prog *= MALLEABLE_MULTIPLIER
            
            efficiency = np.float32(POTENCIES[action])

            if (action == Action.byregots_blessing):
                efficiency += (20 * self.inner_quiet)
            
            #check IQ stacks
            efficiency *= (1 + self.inner_quiet) / 10

            #check all buffs
            efficiency *= self.__get_prog_buffs()
            efficiency /= 100

            qual *= efficiency
            qual = np.floor(qual).item()

            if (self.quality + qual >= REQUIRED_QUALITY):
                reward += REQUIRED_QUALITY - self.quality
                self.quality = REQUIRED_QUALITY
            else:    
                self.quality += qual
                reward += qual

            self.great_strides = 0

            # update inner quiet stacks
            if (action == Action.byregots_blessing):
                self.inner_quiet = 0
            elif (action in ACTION_TYPE.EXTRA_INNER_QUIET):
                self.inner_quiet += 2
            else:
                self.inner_quiet += 1

            if (self.inner_quiet > 10):
                self.inner_quiet = 10

        if (action in ACTION_TYPE.PROGRESS):
            prog = calc_base_progress()
            
            # apply malleable
            if (self.condition == Condition.malleable):
                prog *= GOOD_MULTIPLIER
            
            efficiency = np.float32(POTENCIES[action])
            
            #check all buffs
            efficiency *= self.__get_prog_buffs()
            efficiency /= 100

            prog *= efficiency
            prog = np.floor(prog).item()

            if (self.progress + prog >= REQUIRED_PROGRESS):
                if (self.final_appraisal):
                    reward += REQUIRED_PROGRESS - self.progress - 1
                    self.progress = REQUIRED_PROGRESS - 1
                else:
                    reward = REQUIRED_PROGRESS - self.progress
                    self.progress = REQUIRED_PROGRESS
                    return (reward, True)
            else:    
                self.progress += prog
                reward += prog

            self.muscle_memory = 0

            if (action == Action.muscle_memory):
                self.muscle_memory = MUSCLE_MEMORY_LENGTH

        # durability changes, combo actions


        # change condition and decrement buffs
        self.condition = Condition.RANDOM()
        self.__decrement_buffs()

    def __get_prog_buffs(self) -> int:
        buff = 100

        if (self.veneration > 0):
            buff += 50
        if (self.muscle_memory > 0):
            buff += 100

        return buff

    def __get_qual_buffs(self) -> int:
        buff = 100

        if (self.innovation > 0):
            buff += 50
        if (self.great_strides > 0):
            buff += 100

        return buff


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

    