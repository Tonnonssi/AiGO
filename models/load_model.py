import torch
from network.resnet import *
from utils.saveLoad import *

model = Network(N_RESIDUAL_BLOCK, N_KERNEL, STATE_DIM, N_ACTIONS)
params = torch.load(f"models/model.pth", 
                    weights_only=False,
                    map_location=torch.device('cpu'))
model.load_state_dict(params)
