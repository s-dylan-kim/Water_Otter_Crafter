import torch
import torch.nn as nn
import torch.distributions as D

class PPO2(nn.Module):
    def __init__ (self, input_dim, hidden_dim, output_dim):
        super(PPO2, self).__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        self.network = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.LeakyReLU()
        )

        self.policy_head = nn.Linear(self.hidden_dim, self.output_dim)
        self.value_head = nn.Linear(self.hidden_dim, 1)

    def forward (self, x, action=None):
        shared_nn = self.network(x)
        actor_logit = self.policy_head(shared_nn)
        value = self.value_head(shared_nn)

        distribution = D.categorical.Categorical(logits = actor_logit)

        if action is None:
            action = distribution.sample()
            neg_log_prob = distribution.log_prob(action) * -1
            entropy = distribution.entropy()
        else:
            neg_log_prob = distribution.log_prob(action) * -1
            entropy = distribution.entropy()

        return value, action, neg_log_prob, entropy

    def loss (self, reward, value, advantage, neg_log_prob, entropy, old_value, old_neg_log_prob, clip_range, entropy_coef, value_coef):
        entropy_mean = entropy.mean()
        
        clipped_value = old_value + torch.clamp(value - old_value, min = -clip_range, max=clip_range)

        # unclipped value loss
        value_loss_1 = (value - reward) ** 2
        # clipped value loss
        value_loss_2 = (clipped_value - reward) ** 2

        value_loss = 0.5 * torch.mean(torch.max(value_loss_1, value_loss_2))


        ratio = torch.exp(old_neg_log_prob- neg_log_prob)

        # unclipped policy loss
        policy_loss_1 = -advantage * ratio
        # clipped policy loss
        policy_loss_2 = -advantage * torch.clamp(ratio, 1.0 - clip_range, 1.0 + clip_range)

        policy_loss = torch.mean(torch.max(policy_loss_1, policy_loss_2))

        approxkl = 0.5 * torch.mean((neg_log_prob- old_neg_log_prob)**2)

        # clipfrac = (torch.abs(ratio - 1.0)> clip_range).float().mean()

        loss = policy_loss - entropy_mean * entropy_coef + value_loss * value_coef

        return loss, policy_loss, value_loss, entropy_mean, approxkl