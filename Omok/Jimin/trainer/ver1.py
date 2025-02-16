import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import numpy as np
import random

from utils.setDevice import *
from main.config import *

class TrainNetwork:
    '''
    TrainNetwork(model : nn.Module, batch_size : int, learning_rate : float, learn_decay : float, learn_epoch : int)

    This class conducts training nn. 
    '''
    def __init__(self, model, batch_size, learning_rate, learn_decay, learn_epoch):
        # define
        self.losses = [] # elements : ( p_loss, v_loss )
        self.batch_size = batch_size

        # model & device
        self.model = model
        self.device = next(model.parameters()).device

        # learning rate
        self.init_learning_rate = learning_rate
        self.learn_decay = learn_decay
        self.learn_epoch = learn_epoch

        # Optimizer & Scheduler
        self.L2, self.eps = L2, 1e-4
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.init_learning_rate, weight_decay=self.L2) # eps=self.eps
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=self.learn_epoch, gamma=self.learn_decay)


    def _train(self, history):

        # Sampling
        sample = random.sample(history, self.batch_size)
        states, target_policies, target_values = zip(*sample)

        states = torch.tensor(np.array(states), dtype=torch.float32, device=device).view(self.batch_size, -1, *STATE_SHAPE)  # (BATCH, STATE_DIM, *STATE_SHAPE)
        target_policies = torch.tensor(np.array(target_policies), dtype=torch.float32, device=device).view(self.batch_size, -1)  # (BATCH, N_ACTIONS)
        target_values = torch.tensor(np.array(target_values), dtype=torch.float32, device=device).view(self.batch_size, -1)  # (BATCH, 1)

        # Train Start 
        self.model.train()

        raw_policy, value = self.model(states)

        # Corrected loss calculations
        # p_loss = self.cross_entropy_loss(raw_policy, target_policies)
        # p_loss = F.kl_div(raw_policy.log(), target_policies, reduction='batchmean')

        # cross entropy 
        log_p = torch.log(raw_policy)
        p_loss = -torch.mean(torch.sum(target_policies * log_p, 1))

        # mse loss 
        v_loss = F.mse_loss(value, target_values)

        total_loss = p_loss + v_loss

        # Logging losses
        self.losses.append((p_loss.detach().cpu().item(), v_loss.detach().cpu().item(), total_loss.detach().cpu().item()))

        # Backpropagation
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()


    def __call__(self, history):
        print("")
        print("> Train Started.")
        for i in range(TRAIN_EPOCHS):
            self._train(history)

            if (i+1) % (TRAIN_EPOCHS // 10) == 0:
                p_losses, v_losses, total_losses = zip(*self.losses)
                print(f"step : {i+1} / {TRAIN_EPOCHS} | (mean) p_loss : {np.mean(p_losses[-(TRAIN_EPOCHS // 10):]):.3f} v_loss : {np.mean(v_losses[-(TRAIN_EPOCHS // 10):]):.3f} | lr : {self.scheduler.get_last_lr()}")

        print("> Train Ended.")
        self.scheduler.step()
        

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())
        

if __name__=="__main__":
    print("success.")