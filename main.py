from optparse import Values
import numpy as np
from ppo import PPO2
from crafting_sim.crafting_sim import Crafting_State
from crafting_sim.crafting_types import Action
import torch
# from visdom import Visdom
# import os


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

N_STEP = 2048
GAMMA = 0.99
LAMBDA = 0.95

MINI_BATCHES = 4
N_TRAIN_EPOCH = 4
N_BATCH_TRAIN = (N_STEP // MINI_BATCHES)

CLIP_RANGE = 0.1
VALUE_COEF = 0.5
ENTROPY_COEF = 0.01
MAX_GRAD_NORM = 0.5

LOGS_EVERY = 10

# VIS = Visdom()

def generate_minibatches(model):
    crafting_instance = Crafting_State()

    mb_obs, mb_rewards, mb_actions, mb_values, mb_done, mb_neg_log_prob = [],[],[],[],[],[]
    # epinfos = []

    done = False

    for _ in range (N_STEP):
        obs = np.expand_dims(crafting_instance.to_vector(), 0)

        model.eval()
        with torch.set_grad_enabled(False):
            value, action, neg_log_prob, entropy = model(torch.tensor(obs).to(device))
        action = action.cpu().item()
        neg_log_prob = neg_log_prob.cpu().item()
        value = value.cpu().item()

        mb_obs.append(obs.tolist())
        mb_actions.append(action)
        mb_values.append(value)
        mb_done.append(done)
        mb_neg_log_prob.append(neg_log_prob)

        reward, done = crafting_instance.crafting_sim(Action(action+1)) # +1 due to 1 indexing of enum
        
        mb_rewards.append(reward)
    
    mb_obs = np.squeeze(np.asarray(mb_obs, dtype=np.float32), axis=1)
    mb_rewards = np.asarray(mb_rewards, dtype=np.float32)
    mb_actions = np.asarray(mb_actions)
    mb_values = np.asarray(mb_values, dtype=np.float32)
    mb_neg_log_prob = np.asarray(mb_neg_log_prob, dtype=np.float32)
    mb_done = np.asarray(mb_done, dtype=bool)

    obs = np.expand_dims(crafting_instance.to_vector(), 0)

    # clean up later
    model.eval()
    with torch.set_grad_enabled(False):
        last_value, _, _, _ = model(torch.tensor(obs).to(device))
    last_value = last_value.cpu().item()

    mb_advs = np.zeros_like(mb_rewards)
    gaelambda = 0
    for i in reversed(range(N_STEP)):
        if i == N_STEP - 1:
            done_state = done
            next_val = last_value
        else:
            done_state = mb_done[i+1]
            next_val = mb_values[i+1]

        delta = mb_rewards[i] + GAMMA * next_val * (1 - done_state) - mb_values[i]

        gaelambda = delta + GAMMA * LAMBDA * (1 - done_state) * gaelambda
        mb_advs[i] = gaelambda
    
    mb_returns = mb_advs + mb_values

    return mb_obs, mb_returns, mb_done, mb_actions, mb_values, mb_neg_log_prob
            
            
def train_step_fn(obs, returns, dones, old_actions, old_values, old_neg_log_prbs, model):

    assert old_neg_log_prbs.min() > 0

    obs = torch.tensor(obs).float().to(device)
    returns = torch.tensor(returns).float().to(device)
    old_values = torch.tensor(old_values).float().to(device)
    old_neg_log_prbs = torch.tensor(old_neg_log_prbs).float().to(device)
    old_actions = torch.tensor(old_actions).to(device)

    with torch.set_grad_enabled(False):
        advantages = returns - old_values
        # Normalize the advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    model.train()
    with torch.set_grad_enabled(True):
        model.zero_grad()

        value_f, actions, neg_log_probs, entropy = model(obs, action=old_actions)

        assert(actions.sum().item() == old_actions.sum().item())

        loss, pg_loss, value_loss, entropy_mean, approx_kl = model.loss(returns, value_f, neg_log_probs, entropy, advantages,
                                                                            old_values, old_neg_log_prbs,
                                                                            CLIP_RANGE, ENTROPY_COEF, VALUE_COEF)
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
        optimizer.step()

    return list(map(lambda x: x.detach().item(), [loss, pg_loss, value_loss, entropy_mean, approx_kl]))


# def plot_lines(vals, legend, idx, name):
#     if idx == 1:
#         update=None
#     else:
#         update='append'

#     VIS.line(X=[idx-1],
#              Y=[vals],
#              win=EXP_NAME + "_" + name,
#              opts=dict(
#                  legend=legend,
#                  showlegend=True),
#              update=update)

if __name__ == '__main__':

    # input space 20
    # output space 32

    model = PPO2(20, 32, 32)

    model.to(device)

    optimizer = torch.optim.Adam(model.parameters()) # TODO: ADD LR


    for update in range(1, 100): # number of updates
        obs, returns, done, actions, value, neg_log_prob = generate_minibatches(model)

        mb_loss_vals = []

        ind = np.arange(N_STEP)
        for _ in range(N_TRAIN_EPOCH):
            for start in range(0, N_STEP, N_BATCH_TRAIN):
                end = start + N_BATCH_TRAIN
                mbinds = ind[start:end]

                slices = (arr[mbinds] for arr in (obs, returns, done, actions, value, neg_log_prob))
                loss, policy_loss, value_loss, entropy, approx_k1 = train_step_fn(*slices, model)
                mb_loss_vals.append([loss, policy_loss, value_loss, entropy, approx_k1])

        # Feedforward --> get losses --> update
        loss_vals = np.mean(mb_loss_vals, axis=0)
        loss_names = ['loss', 'policy_loss', 'value_loss', 'policy_entropy', 'approxkl']

        # if update % LOGS_EVERY == 0 or update == 1:
        #     # Calculates if value function is a good predicator of the returns (ev > 1)
        #     # or if it's just worse than predicting nothing (ev =< 0)
        #     print("misc/n_updates", update)
        #     print("misc/total_timesteps", update * N_STEP)

        #     # ep_rew_mean = helper.safemean([ep_info['r'] for ep_info in ep_info_buf])
        #     # ep_len_mean = helper.safemean([ep_info['l'] for ep_info in ep_info_buf])

        #     # print('ep_rew_mean', ep_rew_mean)
        #     # print('ep_len_mean', ep_len_mean)

        #     for (loss_val, loss_name) in zip(loss_vals, loss_names):
        #         print('loss/' + loss_name, loss_val)

        #     plot_lines(loss_vals,  loss_names, update, 'losses')
        #     # plot_lines([ep_rew_mean, ep_len_mean], ['reward', 'length'], update, 'rewards')


        # if update % args.save_every == 0 or update == 1:
        #     # save model checkpoint
        #     torch.save({
        #         'update': update,
        #         'state_dict': model.state_dict(),
        #         'optimizer': optimizer.state_dict()
        #     },
        #         os.path.join("./saves", VERSION, "train_net.cpt")
        #     )

