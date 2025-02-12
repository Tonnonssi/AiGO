import sys 
import os

import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.config import *

# ======== 합성곱 레이어 ===========
class ConvLayer(nn.Module):
    def __init__(self, state_dim, n_kernel):
        super().__init__()
        self.conv = nn.Conv2d(state_dim, n_kernel, kernel_size=3, padding=1, bias=False)
        self.bn = nn.BatchNorm2d(n_kernel)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = F.relu(x)
        return x
    

# ========= 잔차 블럭 =============
class ResidualBlock(nn.Module):
    def __init__(self, n_kernel=N_KERNEL):
        super().__init__()
        self.conv1 = nn.Conv2d(n_kernel, n_kernel, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(n_kernel)
        self.conv2 = nn.Conv2d(n_kernel, n_kernel, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(n_kernel)

    def forward(self, x):
        residual = x

        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x) # double check
        x = self.conv2(x)
        x = self.bn2(x)

        x += residual
        x = F.relu(x)

        return x
    

# ========= ResNet ===========
class Network(nn.Module):
    def __init__(self, n_residual_block, n_kernel, state_dim, n_actions):
        super().__init__()
        self.n_residual_block = n_residual_block
        self.n_kernel = n_kernel
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.n_fc_nodes = n_kernel 

        # nn
        self.conv_layer = ConvLayer(self.state_dim, self.n_kernel)
        self.residual_blocks = nn.Sequential(*[ResidualBlock(self.n_kernel) for _ in range(self.n_residual_block)])
        self.global_pooling = nn.AdaptiveAvgPool2d(1)

        # heads and softmax ftn for policy
        self.policy_head = nn.Linear(self.n_fc_nodes, self.n_actions)
        self.value_head = nn.Linear(self.n_fc_nodes, 1)
        self.softmax = nn.Softmax(dim=-1)
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.conv_layer(x)
        x = self.residual_blocks(x)
        x = self.global_pooling(x)
        x = x.view(x.size(0), -1)  # Flatten

        p, v = self.policy_head(x), self.value_head(x)
        p, v = self.softmax(p), self.tanh(v) # 확률로 변환

        return p, v
    

if __name__=="__main__":
    model = Network(N_RESIDUAL_BLOCK, N_KERNEL, 2, N_ACTIONS)

    # example
    x = torch.randn((128,2,*STATE_SHAPE), requires_grad=True)

    # policy and value
    p, v = model(x)
    p, v = p.detach().numpy(), v.detach().numpy()

    print(f"p.shape : {p.shape}, v.shape : {v.shape}")
    print(f"Policy is \n {p}")
    print(f"value is \n {v}")