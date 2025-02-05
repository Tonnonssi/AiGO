import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import numpy as np
import random

from main.setDevice import *
from main.gameInfo import *

class TrainNetwork:
    def __init__(self, model, batch_size, learning_rate, learn_decay, learn_epoch):
        # define
        self.losses = [] # elements : ( p_loss, v_loss )
        self.batch_size = batch_size
        self.epoch = None

        # model & device
        self.model = model
        self.device = next(model.parameters()).device

        # learning rate
        self.init_learning_rate = learning_rate
        self.learn_decay = learn_decay
        self.learn_epoch = learn_epoch

        # define loss ftn
        self.mse_loss = F.mse_loss
        self.cross_entropy_loss = nn.CrossEntropyLoss()

        # Optimizer & Scheduler
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.init_learning_rate, eps=1e-4, weight_decay=1e-4) # L2 정규화 포함
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=self.learn_epoch, gamma=self.learn_decay)


    def _train(self, history, epoch):

        # Sampling
        sample = random.sample(history, self.batch_size)
        states, target_policies, target_values = zip(*sample)

        states = torch.tensor(np.array(states), dtype=torch.float32).view(self.batch_size, -1, *STATE_SHAPE)  # (BATCH, STATE_DIM, 3, 3)
        target_policies = torch.tensor(np.array(target_policies), dtype=torch.float32).view(self.batch_size, -1)  # (BATCH, 9)
        target_values = torch.tensor(np.array(target_values), dtype=torch.float32).view(self.batch_size, -1)  # (BATCH, 1)

        # device에 올리기
        states, target_policies, target_values = states.to(self.device), target_policies.to(self.device), target_values.to(self.device)

        self.model.train()

        raw_policy, value = self.model(states)

        # Corrected loss calculations
        # p_loss = self.cross_entropy_loss(raw_policy, target_policies)
        p_loss = F.kl_div(F.log_softmax(raw_policy, dim=1), target_policies, reduction='batchmean')
        v_loss = self.mse_loss(value, target_values)

        total_loss = p_loss + v_loss

        # Logging losses
        self.losses.append((p_loss.detach().cpu().item(), v_loss.detach().cpu().item(), total_loss.detach().cpu().item()))

        # Backpropagation
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        # epoch이 업데이트되었다면, 
        if self.epoch != epoch:
            if self.epoch is not None:
                self.scheduler.step()
                self.epoch = epoch               
            else:
                self.epoch = 0

    def __call__(self, history, epoch):
        self._train(history, epoch)

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())
        

if __name__=="__main__":
    print("success.")