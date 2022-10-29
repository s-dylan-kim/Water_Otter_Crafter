from crafting_sim import Crafting_State
from constants import Action

print(["{}: {}".format(action.name, action.value) for action in Action])


test = Crafting_State()

done = False

while(not done):
    print(test)

    input_action = int(input("Enter Action #:\n"))

    print("using: {}\n".format((Action(input_action)).name))

    reward, done = test.crafting_sim(Action(input_action))

    print("reward: {}\n".format(reward))
