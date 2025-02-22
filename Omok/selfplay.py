from collections import deque
from abc import ABC, abstractmethod

from config import *
from Omok.state import *
from Omok.MCTS import *
from utils.transpose_state import *

State = select_state(STATE_DIM)

class Selfplay(ABC):
    '''
    SelfPlay(model : nn.Module, temp : float, n_selfplay : int, n_playout : int)

    The SelfPlay class conducts selfplay of AlphaZero. 
    '''
    def __init__(self, model, temp, n_selfplay, n_playout):
        # model
        self.model = model

        # params
        self.n_selfplay = n_selfplay
        self.n_playout = n_playout

        #  temps
        self.temp = temp

        # selfPlay's yield
        self.history = deque(maxlen=MEM_SIZE)
        self.n_steps = []

        # mcts instance should reset 
        self.mcts = None 

        
    def get_first_player_value(self, ended_state):
        '''
         _get_first_player_point(ended_state : class) -> game_result : float 
         
         game_result = 1  : if first player wins
         game_result = -1 : if first player defeats
         game_result = 0  : if player draws
        '''
        if ended_state.is_lose():
            return -1 if ended_state.is_first_player() else 1
        return 0
    
    @abstractmethod
    def _single_play(self):
        '''
        _single_play() -> None

        This method perform single play which is part of self play. 
        '''
        pass

    def _self_play(self):
        '''
        _self_play() -> None
            > print : 10 idx during game 

        This method performs self play to make history for nn training.
        '''
        for i in range(self.n_selfplay):
            self._single_play()
            print(f"self play :  {self.idx * self.n_selfplay + i+1} / {TOTAL_SELFPLAY} | n_steps : {self.n_steps[-1]}")

    def __call__(self, idx):
        self.idx = idx
        self.mcts = MCTS(self.n_playout)
        self._self_play()

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())

    def _get_transposed_history(self, hist):
        state, policy, value = hist
        policy = policy.reshape(-1,*STATE_SHAPE)
        states_lst = [ftn(state) for ftn in rotate_ftns]
        policy_lst = [ftn(policy).reshape(-1) for ftn in rotate_ftns]
        value_lst = [value] * len(rotate_ftns)
        
        for h in zip(states_lst, policy_lst, value_lst):
            self.history.append(h)

def get_selfplay_class():
    class UnregulatedSelfplay(Selfplay):
        def _single_play(self):
            # single play info 
            history = []
            n_steps = 0
            
            # simulation 
            state = State()

            while True:
                if state.is_done():
                    break

                # get policy of current state 
                learned_policy = np.zeros([state.n_actions]) 

                legal_actions = state.get_legal_actions()
                legal_policy = np.array(self.mcts.get_legal_policy(state, self.model, self.temp))

                nosie = np.random.dirichlet(0.3*np.ones(len(legal_policy)))
                legal_policy = 0.75*legal_policy + 0.25*nosie

                learned_policy[legal_actions] = legal_policy
                
                history.append([state(), learned_policy, None]) 

                # get legal action 
                action = np.random.choice(legal_actions, p=legal_policy)

                # step
                state = state.next(action)
                n_steps += 1 

            # ====== history : update whole value ======
            value = self.get_first_player_value(state)

            for idx in range(len(history)):
                history[idx][-1] = value
                self._get_transposed_history(history[idx])
                self.history.append(history[idx])
                # reverse value 
                value = -value

            # update self.n_steps
            self.n_steps.append(n_steps)

    class RegulatedSelfplay(Selfplay):
        def _single_play(self):
            # single play info 
            history = []
            n_steps = 0
            
            # simulation 
            state = State()

            while True:
                if state.is_done():
                    break

                # get policy of current state 
                learned_policy = np.zeros([state.n_actions]) # init value
                legal_actions = state.get_legal_actions()

                if n_steps < EXPLORE_REGULATION:
                    legal_policy = np.array(self.mcts.get_legal_policy(state, self.model, self.temp))

                else:
                    legal_policy = self.mcts.get_legal_policy(state, self.model, 0) 

                nosie = np.random.dirichlet(0.3*np.ones(len(legal_policy)))
                legal_policy = 0.75*legal_policy + 0.25*nosie
                learned_policy[legal_actions] = legal_policy
                
                history.append([state(), learned_policy, None]) 

                # get legal action 
                action = np.random.choice(legal_actions, p=legal_policy)

                # step
                state = state.next(action)
                n_steps += 1 

            # ====== history : update whole value ======
            value = self.get_first_player_value(state)

            for idx in range(len(history)):
                history[idx][-1] = value
                self._get_transposed_history(history[idx])
                self.history.append(history[idx])
                # reverse value 
                value = -value

            # update self.n_steps
            self.n_steps.append(n_steps)

    if EXPLORE_REGULATION is None:
        return UnregulatedSelfplay
    else:
        return RegulatedSelfplay