import matplotlib.pyplot as plt

from config import *
from Omok.MCTS import *
from Omok.state import *
from utils.valid_tool import *

# select state 
State = select_state(STATE_DIM)

class ModelvsHuman:
    '''
    This class conducts model vs human game. 
    '''
    def __init__(self, model):
        self.model = model
        self.mcts = MCTS(N_PLAYOUT)
        self.get_next_actions = self.mcts.get_legal_actions_of(model, 0, with_policy=True)

    def vs_human(self, with_policy=True):
        '''
        vs_human(self, with_policy : bool)
            > print : model's action as coord
            > print : human's action as coord
            > print : (state, policy, n_visit) visualization
            > print : (state, _, _) visualization
        '''
        def flatten_idx(coord):
            return coord[0] * STATE_SHAPE[1] + coord[1]
        
        state = State()

        while True:
            if state.is_done():
                break

            # MCTS actions 
            action, policy, n_visits = self.get_next_actions(state)
            x, y = divmod(action, STATE_SHAPE[1])
            print(f"Alpha Zero's Action is : {(int(x), int(y))}")

            if  with_policy:
                visualize_pack('best', state(), n_visits, policy, action)

            state = state.next(action)

            # Player actions
            x, y = map(int, input("Enter coordinates (x,y): ").split(','))
            print(f"My action is ({x}, {y})")
            my_action = flatten_idx((x,y))
            prev_state = copy.deepcopy(state)
            state = state.next(my_action)
            
            if state.is_done():
                _, axes = plt.subplots(1, 3, figsize=(18, 6))

                draw_omok_board(prev_state(), next_action=my_action, ax=axes[0])
            
                plt.tight_layout()
                plt.suptitle("Human's Turn", fontsize=26, fontweight='bold', y=1.02)

            

    def __call__(self, with_policy=True):
        self.vs_human(with_policy)