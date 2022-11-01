from crafting_sim import Crafting_State
from crafting_types import Action, Condition

# print(["{}: {}".format(action.name, action.value) for action in Action])
# print(["{}: {}".format(condition.name, condition.value) for condition in Condition])

test = Crafting_State()

done = False

while(not done):
    print(test)

    input_action = input("Enter Action #:\n")

    print("using: {}\n".format(input_action))

    reward, done = test.crafting_sim(Action[input_action])

    # input_condition = input("Enter condition #:\n")

    # test.set_condition(Condition[input_condition])

    # print("using: {}\n".format(input_condition))

    print("reward: {}\n".format(reward))
