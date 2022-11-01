from random import random
import crafting_sim.constants as constants
from crafting_sim.crafting_types import Condition, Action
from crafting_sim.utils import calc_base_progress, calc_base_quality
from math import floor
import numpy as np
import torch

class Crafting_State:
    def __init__(self):
        ############    States for actions (buffs/combos)       ############

        # combo states
        self.touch_combo = 0 # 0: no combo, 1: after basic touch, 2: after standard touch
        self.observe = False # combo for focused synth/touch
        self.inner_quiet = 0
        
        # steps left on each buff
        self.waste_not_1 = 0
        self.waste_not_2 = 0
        self.manipulation = 0
        self.great_strides = 0
        self.veneration = 0
        self.innovation = 0
        self.final_appraisal = 0
        self.muscle_memory = 0

        # uses left on specialist actions
        self.careful_observation = constants.CAREFUL_OBSERVATION_USES
        self.heart_and_soul = constants.HEART_AND_SOUL_USES

        # state for starting actions (reflect/muscle memory)
        self.initial = True
        self.heart_and_soul_on = False

        ############     States for Craft (progress/condition)     ############
        self.progress = 0
        self.quality = 0
        self.cp = constants.INITIAL_CP
        self.condition = Condition.normal
        self.durability = constants.STARTING_DURABILITY

    def __str__(self):
        str_list = []
        str_list.append("progress: {}\n".format(self.progress))
        str_list.append("quality: {}\n".format(self.quality))
        str_list.append("CP: {}\n".format(self.cp))
        str_list.append("Condition: {}\n".format(self.condition))
        str_list.append("Durability: {}\n\n".format(self.durability))

        str_list.append("Buffs\nWaste Not 1: {}\n".format(self.waste_not_1))
        str_list.append("Waste Not 2: {}\n".format(self.waste_not_2))
        str_list.append("Manipulation: {}\n".format(self.manipulation))
        str_list.append("Great Strides: {}\n".format(self.great_strides))
        str_list.append("Veneration: {}\n".format(self.veneration))
        str_list.append("Innovation: {}\n".format(self.innovation))
        str_list.append("Final Appraisal: {}\n".format(self.final_appraisal))
        str_list.append("Muscle Memory: {}\n\n".format(self.muscle_memory))

        str_list.append("Other\nInner Quiet: {}\n".format(self.inner_quiet))
        str_list.append("Touch Combo: {}\n".format(self.touch_combo))
        str_list.append("Observe: {}\n".format(self.observe))
        str_list.append("Heart and Soul: {}\n".format(self.heart_and_soul_on))

        return ''.join(str_list)

    def to_vector(self):
        out = np.empty(20, dtype=np.float32)
        out[0] = self.progress / constants.REQUIRED_PROGRESS
        out[1] = self.quality / constants.REQUIRED_QUALITY
        out[2] = self.cp / constants.INITIAL_CP
        out[3] = self.condition.value / len(Condition)
        out[4] = self.durability / constants.STARTING_DURABILITY

        out[5] = self.touch_combo / 2 # 3 steps
        out[6] = self.observe
        out[7] = self.inner_quiet / 10

        out[8] = self.waste_not_1 / (constants.WASTE_NOT_1_LENGTH + 2) # +2 for primed
        out[9] = self.waste_not_2 / (constants.WASTE_NOT_2_LENGTH + 2)
        out[10] = self.manipulation / (constants.MANIPULATION_LENGTH + 2)
        out[11] = self.great_strides / (constants.GREAT_STRIDES_LENGTH + 2)
        out[12] = self.veneration / (constants.VENERATION_LENGTH + 2)
        out[13] = self.innovation / (constants.INNOVATION_LENGTH + 2)
        out[14] = self.final_appraisal / (constants.FINAL_APPRAISAL_LENGTH + 2)
        out[15] = self.muscle_memory / (constants.MUSCLE_MEMORY_LENGTH + 2)
        out[16] = self.careful_observation / constants.CAREFUL_OBSERVATION_USES
        out[17] = self.heart_and_soul / constants.HEART_AND_SOUL_USES
        out[18] = self.heart_and_soul_on
        out[19] = self.initial

        return out


    def crafting_sim(self, action: Action) -> tuple[int, bool]:  # returns (reward, done?)
        # check action validity
        # check first actions
        if (action in constants.ACTION_TYPE.INITIAL_ACTIONS and not self.initial):
            return (-100, False)

        #check limited use actions
        if (action == Action.careful_observation and self.careful_observation <= 0 or action == Action.heart_and_soul and self.heart_and_soul <= 0):
            return (-100, False)

        # check good actions
        if ((self.condition != Condition.good and not self.heart_and_soul_on) and action in constants.ACTION_TYPE.GOOD_ACTIONS):
            return (-100, False)
        
        # check half durability actions
        if ((self.waste_not_1 > 0 or self.waste_not_2 > 0) and action in constants.ACTION_TYPE.HALF_DURABILITY):
            return (-100, False)

        # check traained inesse
        if (action == Action.trained_finesse and self.inner_quiet < 10):
            return (-100, False)

        # check CP cost
        cp_cost = constants.CP_COST[action.value]
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
            if (action == Action.heart_and_soul):
                self.heart_and_soul -= 1
                self.heart_and_soul_on = True
            if (action == Action.careful_observation):
                self.careful_observation -= 1
                self.condition = Condition.RANDOM()
            return (0, False)

        # track reward
        reward = 0
        done = False

        action_fail = False


        # check if actions succeeds
        if (action in constants.ACTION_TYPE.CHANCE_OF_FAIL and
                not (self.observe and action in constants.ACTION_TYPE.OBSERVE_ACTIONS)):
            random_roll = random()
            if (constants.SUCCESS[action.value] < random_roll or self.condition == Condition.centered and constants.SUCCESS[action.value] * 1.25 < random_roll):
                action_fail = True
        
        self.initial = False
        self.heart_and_soul_on = False
        self.observe = False

        if (not action_fail):
            # calc quality and progress changes
            if (action in constants.ACTION_TYPE.QUALITY):
                reward += self.__change_qual(action)

            if (action in constants.ACTION_TYPE.PROGRESS):
                reward += self.__change_prog(action)
                
                ## add extra incentive for completing craft
                if (self.progress >= constants.REQUIRED_PROGRESS):
                    if (self.quality >= constants.REQUIRED_QUALITY):
                        reward += 1000
                    return (reward, True)

        # hand combo actions
        if (action == Action.observe):
            self.observe = True
        if (action == Action.basic_touch):
            self.touch_combo = 1
        elif (action == Action.standard_touch and self.touch_combo == 1):
            self.touch_combo = 2
        else:
            self.touch_combo = 0

        if (action not in constants.ACTION_TYPE.BUFF_ACTIONS):
            # durability changes
            done = self.__change_durability(action)

        # check manipulation
        if (self.manipulation > 0):
            self.durability += constants.MANIPULATION_DURABILITY

        self.__decrement_buffs()

        if (action in constants.ACTION_TYPE.BUFF_ACTIONS):
            # check buff actions
            reward += self.__apply_buffs(action)
            
            

        # check for overcap
        if (self.durability > constants.STARTING_DURABILITY):
            self.durability = constants.STARTING_DURABILITY

        # change condition and decrement buffs
        self.condition = Condition.RANDOM()
        return (reward, done)


    def __change_qual(self, action: Action) -> int:
        reward = 0

        qual = calc_base_quality()

        # apply malleable
        if (self.condition == Condition.good):
            qual *= constants.GOOD_MULTIPLIER

        efficiency = np.float32(constants.POTENCIES[action.value])/100

        if (action == Action.byregots_blessing):
            efficiency += (0.2 * self.inner_quiet)
        
        #check IQ stacks
        efficiency *= 1 + self.inner_quiet / 10

        #check all buffs
        efficiency *= self.__get_qual_buffs()
        efficiency /= 100

        qual *= efficiency
        qual = int(np.floor(qual).item())

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
        
        efficiency = np.float32(constants.POTENCIES[action.value])/100
        
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
                return reward
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

        if action == Action.waste_not_1:
            if (self.waste_not_1 > constants.WASTE_NOT_1_LENGTH + additional_turns):
                return -100
            else:
                self.waste_not_1 = constants.WASTE_NOT_1_LENGTH + additional_turns
        elif action == Action.waste_not_2:
            if (self.waste_not_2 > constants.WASTE_NOT_2_LENGTH + additional_turns):
                return -100
            else:
                self.waste_not_2 = constants.WASTE_NOT_2_LENGTH + additional_turns
        elif action == Action.manipulation:
            if (self.manipulation > constants.MANIPULATION_LENGTH + additional_turns):
                return -100
            else:
                self.manipulation = constants.MANIPULATION_LENGTH + additional_turns
        elif action == Action.great_strides:
            if (self.great_strides > constants.GREAT_STRIDES_LENGTH + additional_turns):
                return -100
            else:
                self.great_strides = constants.GREAT_STRIDES_LENGTH + additional_turns
        elif action == Action.veneration:
            if (self.veneration > constants.VENERATION_LENGTH + additional_turns):
                return -100
            else:
                self.veneration = constants.VENERATION_LENGTH + additional_turns
        elif action == Action.innovation:
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
        if (self.waste_not_1 or self.waste_not_2):
            durability_change /= 2
        if (action == Action.masters_mend):
            durability_change = 30

        durability_change = floor(durability_change)

        self.durability += durability_change

        return self.durability <= 0

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

    
    # for debug
    def set_condition(self, condition: Condition):
        self.condition = condition