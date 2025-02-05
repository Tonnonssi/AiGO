import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from MCTS.ver1 import *
from main.hyperParams import *
from state.ver2 import *
from visualize.valid_tool import *

class ModelvsHuman:
    def __init__(self, model):
        self.model = model
        self.mcts = MCTS(N_PLAYOUT)
        self.get_next_actions = self.mcts.get_legal_actions_of(model, 0, with_policy=True)

    def vs_human(self, with_policy):
        def flatten_idx(coord):
            return coord[0] * STATE_SHAPE[1] + coord[1]
        
        state = State()

        while True:
            if state.is_done():
                break

            action, policy, n_visits = self.get_next_actions(state)

            if  with_policy:
                visualize_pack('best', state(), n_visits, policy, action)

            state = state.next(action)

            print(f"Alpha Zero's Action is : {action}")

            my_action = int(input("Choose Your Action : "))
            # my_action = flatten_idx(coord)
            state = state.next(my_action)

    def __call__(self, with_policy=True):
        self.vs_human(with_policy)