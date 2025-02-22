import torch
from Omok.Jimin.network.resnet import *
from Omok.Jimin.utils.saveLoad import *

model = Network(N_RESIDUAL_BLOCK, N_KERNEL, STATE_DIM, N_ACTIONS)
params = torch.load(f"/Users/ijimin/Documents/GitHub/AiGO/web/models/latest_model_weight.pth", 
                    weights_only=False,
                    map_location=torch.device('cpu'))
model.load_state_dict(params)
