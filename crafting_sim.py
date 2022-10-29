from random import Random
import constants
from crafting_types import Condition, Action
from utils import calc_base_progress, calc_base_quality
from math import ceil
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
    careful_observation = constants.CAREFUL_OBSERVATION_USES
    heart_and_soul = constants.HEART_AND_SOUL_USES

    # state for starting actions (reflect/muscle memory)
    initial = True

    ############     States for Craft (progress/condition)     ############
    progress = 0
    quality = 0
    cp = constants.INITIAL_CP
    condition = Condition.normal
    durability = constants.STARTING_DURABILITY

    def crafting_sim(self, action: Action) -> tuple[int, bool]:  # returns (reward, done?)
        # check action validity
        # check first actions
        if (action in constants.ACTION_TYPE.INITIAL_ACTIONS and not self.initial):
            return (-100, False)

        # check good actions
        if (self.condition != Condition.good and action in constants.ACTION_TYPE.GOOD_ACTIONS):
            return (-100, False)
        
        # check half durability actions
        if ((self.waste_not_1 > 0 or self.waste_not_2 > 0) and action in constants.ACTION_TYPE.HALF_DURABILITY):
            return (-100, False)

        # check CP cost
        cp_cost = constants.CP_COST[action]
        if (action == Action.standard_touch and self.touch_combo == 1 or action == Action.advanced_touch and self.touch_combo == 2):
            cp_cost = constants.TOUCH_COMBO_CP

        if (self.cp < cp_cost):
            return (-100, False)

        # UPDATE CP
        self.cp -= cp_cost

        # check either of actions that dont progress turns
        if (action in constants.ACTION_TYPE.NO_TURN):
            if (action == Action.final_appraisal):
                self.final_appraisal = constants.FINAL_APPRAISAL_LENGTH
            return (0, False)


        # check if actions succeeds
        if (action in constants.ACTION_TYPE.CHANCE_OF_FAIL):
            if (self.observe and action in constants.ACTION_TYPE.OBSERVE_ACTIONS):
                random = Random.random()
                if (constants.SUCCESS[action] < random or self.condition == Condition.centered and constants.SUCCESS[action] * 1.25 < random):
                    return (0, False)
        
        # track reward
        reward = 0

        # calc quality and progress changes
        if (action in constants.ACTION_TYPE.QUALITY):
            reward += self.__change_qual(action)

        if (action in constants.ACTION_TYPE.PROGRESS):
            reward += self.__change_prog(action)
            
            ## add extra incentive for completing craft
            if (self.progress >= constants.REQUIRED_PROGRESS):
                return (reward, True)

        # check buff actions
        reward += self.__apply_buffs(action)

        # durability changes
        done = self.__change_durability(action)

        # change condition and decrement buffs
        self.condition = Condition.RANDOM()
        self.__decrement_buffs()

        return (reward, done)


    def __change_qual(self, action: Action) -> int:
        reward = 0

        qual = calc_base_quality()
        
        # apply malleable
        if (self.condition == Condition.good):
            prog *= constants.MALLEABLE_MULTIPLIER
        
        efficiency = np.float32(constants.POTENCIES[action])

        if (action == Action.byregots_blessing):
            efficiency += (20 * self.inner_quiet)
        
        #check IQ stacks
        efficiency *= (1 + self.inner_quiet) / 10

        #check all buffs
        efficiency *= self.__get_qual_buffs()
        efficiency /= 100

        qual *= efficiency
        qual = np.floor(qual).item()

        if (self.quality + qual >= constants.REQUIRED_QUALITY):
            reward += constants.REQUIRED_QUALITY - self.quality
            self.quality = constants.REQUIRED_QUALITY
        else:    
            self.quality += qual
            reward += qual

        self.great_strides = 0

        # update inner quiet stacks
        if (action == Action.byregots_blessing):
            self.inner_quiet = 0
        elif (action in constants.ACTION_TYPE.EXTRA_INNER_QUIET):
            self.inner_quiet += 2
        else:
            self.inner_quiet += 1

        if (self.inner_quiet > 10):
            self.inner_quiet = 10

        return reward

    def __change_prog(self, action: Action) -> int:
        reward = 0

        prog = calc_base_progress()
            
        # apply malleable
        if (self.condition == Condition.malleable):
            prog *= constants.GOOD_MULTIPLIER
        
        efficiency = np.float32(constants.POTENCIES[action])
        
        #check all buffs
        efficiency *= self.__get_prog_buffs()
        efficiency /= 100

        prog *= efficiency
        prog = np.floor(prog).item()

        if (self.progress + prog >= constants.REQUIRED_PROGRESS):
            if (self.final_appraisal):
                reward += constants.REQUIRED_PROGRESS - self.progress - 1
                self.progress = constants.REQUIRED_PROGRESS - 1
            else:
                reward = constants.REQUIRED_PROGRESS - self.progress
                self.progress = constants.REQUIRED_PROGRESS
                return (reward, True)
        else:    
            self.progress += prog
            reward += prog

        self.muscle_memory = 0

        if (action == Action.muscle_memory):
            self.muscle_memory = constants.MUSCLE_MEMORY_LENGTH

        return reward
        
    
    def __apply_buffs(self, action: Action) -> int:
        additional_turns = 0
        if (self.condition == Condition.primed):
            additional_turns = constants.PRIMED_ADDITIONAL_TURNS

        match action:
            case Action.waste_not_1:
                if (self.waste_not_1 > constants.WASTE_NOT_1_LENGTH + additional_turns):
                    return -100
                else:
                    self.waste_not_1 = constants.WASTE_NOT_1_LENGTH + additional_turns
            case Action.waste_not_2:
                if (self.waste_not_2 > constants.WASTE_NOT_2_LENGTH + additional_turns):
                    return -100
                else:
                    self.waste_not_2 = constants.WASTE_NOT_2_LENGTH + additional_turns
            case Action.manipulation:
                if (self.manipulation > constants.MANIPULATION_LENGTH + additional_turns):
                    return -100
                else:
                    self.manipulation = constants.MANIPULATION_LENGTH + additional_turns
            case Action.great_strides:
                if (self.great_strides > constants.GREAT_STRIDES_LENGTH + additional_turns):
                    return -100
                else:
                    self.great_strides = constants.GREAT_STRIDES_LENGTH + additional_turns
            case Action.veneration:
                if (self.veneration > constants.VENERATION_LENGTH + additional_turns):
                    return -100
                else:
                    self.veneration = constants.VENERATION_LENGTH + additional_turns
            case Action.innovation:
                if (self.innovation > constants.INNOVATION_LENGTH + additional_turns):
                    return -100
                else:
                    self.innovation = constants.INNOVATION_LENGTH + additional_turns

        return 0


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

    # return whether or not the craft is done
    def __change_durability(self, action: Action) -> bool:
        durability_change = -10

        if (action in constants.ACTION_TYPE.HALF_DURABILITY):
            durability_change /= 2
        if (action in constants.ACTION_TYPE.DOUBLE_DURABILITY):
            durability_change *= 2
        if (self.condition == Condition.sturdy):
            durability_change /= 2
        if (action == Action.masters_mend):
            durability_change = -30
        
        durability_change = ceil(durability_change)

        self.durability += durability_change

        if (self.durability < 0):
            return True

        # check manipulation
        if (self.manipulation > 0):
            self.durability += constants.MANIPULATION_DURABILITY

        # check for overcap
        if (self.durability > constants.STARTING_DURABILITY):
            self.durability = constants.STARTING_DURABILITY
        
        return False

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

    