from state.ver2 import *
from MCTS.ver1 import *
from collections import deque
from main.hyperParams import *

State = select_state(STATE_DIM)

class SelfPlay:
    '''
    SelfPlay(model : nn.Module, temp : float, temp_discount : float, n_selfplay : int, n_playout : int)

    The SelfPlay class conducts selfplay of AlphaZero. 
    '''
    def __init__(self, model, temp, temp_discount, n_selfplay, n_playout):
        # model
        self.model = model

        # params
        self.n_selfplay = n_selfplay
        self.n_playout = n_playout

        # about temps
        self.temp = temp
        self.temp_discount = temp_discount

        # selfPlay's yield
        self.history = deque(maxlen=10000)

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

    def _single_play(self):
        '''
        _single_play() -> None

        This method perform single play which is part of self play. 
        '''
        history = []
        state = State()

        while True:
            if state.is_done():
                break

            # get policy of current state 
            learned_policy = np.zeros([state.n_actions]) # init value

            legal_policy = self.mcts.get_legal_policy(state, self.model, self.temp) 

            learned_policy[state.get_legal_actions()] = legal_policy
            
            history.append([state(), learned_policy, None]) 

            # get legal action 
            action = np.random.choice(state.get_legal_actions(), p=legal_policy)

            # step
            state = state.next(action)

        # ====== history : update whole value ======
        value = self.get_first_player_value(state)

        for idx in range(len(history)):
            history[idx][-1] = value
            self.history.append(history[idx])
            # reverse value 
            value = -value

    def _self_play(self):
        '''
        _self_play() -> None
            > print : 10 idx during game 

        This method performs self play to make history for nn training.
        '''
        for i in range(self.n_selfplay):
            self._single_play()
            if (i+1) % (self.n_selfplay // 10) == 0:
                print(f"self play {i+1} / {self.n_selfplay} ({TOTAL_SELFPLAY})")

    def __call__(self, idx):
        self.mcts = MCTS(self.n_playout)
        self._self_play()
         # discount temp
        self.temp = 1 if idx < 30 else self.temp * self.temp_discount

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())