import sys 
import os

import torch.nn as nn
import torch.nn.functional as F

class BasicNetwork(nn.Module):
    """policy-value network module"""
    def __init__(self, state_dim: int, n_actions: int):
        super().__init__()
        self.n_actions = n_actions
        self.state_dim = state_dim

        # common layers
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        # policy layers
        self.policy_head = nn.Sequential(
            nn.Conv2d(128, state_dim, kernel_size=1),
            nn.BatchNorm2d(state_dim),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(state_dim * n_actions, n_actions),
            nn.Softmax(dim=1)
        )

        # state value layers
        self.value_head = nn.Sequential(
            nn.Conv2d(128, 2, kernel_size=1),
            nn.BatchNorm2d(2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * n_actions, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh()
        )

    def forward(self, state_input):
        # common layers
        x = F.relu(self.bn1(self.conv1(state_input)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))

        # policy layers
        policy = self.policy_head(x)

        # state value layers
        value = self.value_head(x)

        return policy, value