import sys 
import os

import torch.nn as nn
import torch.nn.functional as F

class Network(nn.Module):
    """policy-value network module"""
    def __init__(self, state_dim : int, n_actions : int):
        super().__init__()
        self.n_actions = n_actions
        self.state_dim = state_dim

        # common layers
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        # policy layers
        self.act_conv1 = nn.Conv2d(128, state_dim, kernel_size=1)
        self.act_fc1 = nn.Linear(state_dim*n_actions, n_actions)
        
        # state value layers
        self.val_conv1 = nn.Conv2d(128, 2, kernel_size=1)
        self.val_fc1 = nn.Linear(2*n_actions, 64)
        self.val_fc2 = nn.Linear(64, 1)

    def forward(self, state_input):
        # common layers
        x = F.relu(self.conv1(state_input))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))

        # policy layers
        x_act = F.relu(self.act_conv1(x))
        x_act = x_act.view(-1, self.state_dim*self.n_actions)
        x_act = F.log_softmax(self.act_fc1(x_act))

        # state value layers
        x_val = F.relu(self.val_conv1(x))
        x_val = x_val.view(-1, 2*self.n_actions)
        x_val = F.relu(self.val_fc1(x_val))
        x_val = F.tanh(self.val_fc2(x_val))

        return x_act, x_val