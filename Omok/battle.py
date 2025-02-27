from Omok.MCTS import *
from Omok.state import *
from utils.valid_tool import *
from utils.saveLoad import *

class BattleNN:
    def __init__(self, model_1, model_2, n_selfplay, n_playout, eval_temp, state_type:tuple):
        # model 
        self.model_1 = model_1
        self.model_2 = model_2

        # common params 
        self.n_selfplay = n_selfplay
        self.n_playout = n_playout
        self.eval_temp = eval_temp

        self.mcts = MCTS(n_playout)

        # state class per each model 
        self.State1 = select_state(state_type[0])
        self.State2 = select_state(state_type[1])

        # win-lose count list
        self.first_player_win = [0,0] # nn 1's perspect, nn 2's perspect
        self.n_steps_lst = []
        self.history = []

    def _first_player_point(self, ended_state):
        '''
         _first_player_point(ended_state : class) -> game_result : float 
         
         game_result = 1 : if first player wins
         game_result = 0 : if first player defeats
         game_result = 0.5 : if player draws
        '''
        if ended_state.is_lose():
            return 0 if ended_state.is_first_player() else 1
        return 0.5

    def _evaluate_network(self):
        # use MCTS to select next action 
        next_actions_1 = self.mcts.get_legal_actions_of(self.model_1, self.eval_temp)
        next_actions_2 = self.mcts.get_legal_actions_of(self.model_2, self.eval_temp)
        next_actions = (next_actions_1, next_actions_2)

        for i in range(self.n_selfplay):
            if i % 2 == 0: # first player is nn1
                point = self._single_play(next_actions, current_player=1)
                self.first_player_win[0] += point

            else: # first player is nn2
                point = 1 - self._single_play(list(reversed(next_actions)), current_player=2)
                self.first_player_win[1] += point

            if (i+1) % (self.n_selfplay // 5) == 0:
                print(f"eval game {i+1} / {self.n_selfplay}")

        return self.first_player_win[0] / (self.n_selfplay / 2),  self.first_player_win[1] / (self.n_selfplay / 2),


    def _single_play(self, next_action_methods, current_player=1):
        '''
        _single_play( next_action_methods : list containing methods ) -> point : float 

        This method conducts single game aka single play.
        '''
        n_steps = 0
        epi_history = []

        state1 = self.State1()
        state2 = self.State2()

        while True:
            if state1.is_done():
                break

            get_next_action = next_action_methods[0] if state1.is_first_player() else next_action_methods[1]

            # 둘 중 하나 
            if current_player == 1:
                action = get_next_action(state1)
                state1 = state1.next(action)
                state2 = state2.next(action)
                current_player = 2 # 턴을 넘김 
                epi_history.append(state1)

            elif current_player == 2:
                action = get_next_action(state2)
                state1 = state1.next(action)
                state2 = state2.next(action)
                current_player = 1 # 턴을 넘김 
                epi_history.append(state2)
            
            n_steps += 1

        self.n_steps_lst.append(n_steps)
        self.history.append(epi_history)

        return self._first_player_point(state1)
    
    def __call__(self):
        print("")
        print("> Evaluation Started.")
        return self._evaluate_network()
