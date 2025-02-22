import matplotlib.pyplot as plt

from MCTS.ver1 import *
from state.ver2 import *
from utils.valid_tool import *
from utils.saveLoad import *

State = select_state(STATE_DIM)

class EvalNetwork:
    '''
    EvalNetwork(best_model:nn.Module, eval_selfplay:int, eval_temperature:float, eval_count:int)
    -----------
    The EvalNetwork class manages the evaluation process of a neural network during training. 
    It assesses the performance of a newly trained model (recent_model) against the current best model (best_model) 
    using Monte Carlo Tree Search (MCTS). The class determines whether the recent model should replace the best model 
    based on its performance in multiple evaluation games.

    '''
    def __init__(self, best_model, eval_selfplay, eval_temperature, eval_count, n_actions):
        # eval info
        self.eval_selfplay = eval_selfplay
        self.eval_temperature = eval_temperature

        # models
        self.best_model = best_model
        self.recent_model = None

        # MCTS instance 
        self.mcts = MCTS(eval_count)

        # init value
        self.updated = False
        self.win_rate = 0.0

        # for visualize result
        # game result from recent model sight.
        self.game_result = {'lose' : 0,
                            'draw' : 0,
                            'win' : 0}
        
        self.n_actions = n_actions

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

    def _evaluate_network(self, recent_model):
        '''
        _evaluate_network(recent_model : nn.Module) -> None
            > print : ave point (equal to win rate when draw does not exist.)
        
        This method eval latest model vs best model by alternating the first plater in each game.
        When ave point goes over 0.5(0.55), the best model is updated by latest model. 
        '''
        # init dict
        self.game_result = dict.fromkeys(self.game_result, 0)

        # get network
        self.recent_model = recent_model

        # use MCTS to select next action 
        next_actions_recent = self.mcts.get_legal_actions_of(self.recent_model, self.eval_temperature)
        next_actions_best = self.mcts.get_legal_actions_of(self.best_model, self.eval_temperature)
        next_actions = (next_actions_recent, next_actions_best)

        total_point = 0

        for i in range(self.eval_selfplay):
            if i % 2 == 0: # first player is latest model 
                point = self._single_play(next_actions)
                self.game_result[list(self.game_result.keys())[int(point*2)]] += 1
                total_point += point

            else: # first player is best model 
                point = 1 - self._single_play(list(reversed(next_actions)))
                self.game_result[list(self.game_result.keys())[int(point*2)]] += 1
                total_point += point

            if (i+1) % (self.eval_selfplay // 5) == 0:
                print(f"eval game {i+1} / {self.eval_selfplay}")

        average_point = total_point / self.eval_selfplay

        print('Average Point of Latest Model', average_point)

        # visualize_game_result(self.game_result) # visualize circle graph 

        if average_point >= 0.55:
            self._update_best_model()

        self.win_rate = round(self.game_result['win'] / sum(self.game_result.values()), 2), round((self.game_result['win'] + self.game_result['draw']) / sum(self.game_result.values()), 2)
        print(f"Win rate : {self.win_rate[0]:.2f}")

    def _single_play(self, next_action_methods):
        '''
        _single_play( next_action_methods : list containing methods ) -> point : float 

        This method conducts single game aka single play.
        '''
        state = State()

        while True:
            if state.is_done():
                break

            get_next_action = next_action_methods[0] if state.is_first_player() else next_action_methods[1]

            action = get_next_action(state)
            state = state.next(action)

        return self._first_player_point(state)
    
    def _visualize_game_step(self, next_action_methods:list, first_agent_type='recent', path=None, download=False):
        '''
        _visualize_game_step(next_action_methods:list containing method, first_agent_type='recent', path=None, download=False)
            -> None
            > print : (state-action, MCTS visits, policy) visualization.

        This method conducts self play with visualization.
        It visualizes the state-action, MCTS visits, policy.
        '''
        total_game_steps = []
        type_label = ['best', 'recent'] if first_agent_type == 'recent' else ['recent', 'best']

        state = State()

        for step in range(self.n_actions):
            if state.is_done():
                return total_game_steps

            get_next_action_policy_nvisits = next_action_methods[0] if state.is_first_player() else next_action_methods[1]
            first_agent_type = type_label[int(state.is_first_player())]
            
            action, policy, n_visits = get_next_action_policy_nvisits(state)
            visualize_pack(first_agent_type, state(), n_visits, policy, action, step, path, download)

            total_game_steps.append(action)
            state = state.next(action)

    def visualize_game(self, idx=0, recent_model=None, download=False):
        '''
        visualize_game(idx=0, recent_model=None, download=False)
            > (state-action, MCTS visits, policy) visualization when *latest* model is 1st player.
            > (state-action, MCTS visits, policy) visualization when *best* model is 1st player.
            > Game record of two alertnative 1st player situation. (seq : latest, best)
        '''
        # get network
        self.recent_model = recent_model if recent_model is not None else self.recent_model

        # make dir to save visualizations.
        # valid_f_paths = (valid_f_path, valid_recent_f_path, valid_best_f_path)
        valid_f_paths = make_valid_file_paths(idx) if download else None 

        # use MCTS to select next action.
        next_actions_recent = self.mcts.get_legal_actions_of(self.recent_model, self.eval_temperature, with_policy=True)
        next_actions_best = self.mcts.get_legal_actions_of(self.best_model, self.eval_temperature, with_policy=True)
        next_actions_list = (next_actions_recent, next_actions_best)
        
        # return step history to visualize game record.
        recent_game_record = self._visualize_game_step(next_actions_list, 
                                                       first_agent_type='recent', 
                                                       path=valid_f_paths[1], 
                                                       download=download)
        best_game_record = self._visualize_game_step(list(reversed(next_actions_list)), 
                                                     first_agent_type='best',
                                                     path=valid_f_paths[2], 
                                                     download=download)

        _, axes = plt.subplots(1, 2, figsize=(12, 6))
        visualize_game_record(recent_game_record, ax=axes[0])
        visualize_game_record(best_game_record, ax=axes[1])

        plt.tight_layout()
        plt.suptitle("Game record when the first model is Latest or Best Model.", fontsize=20, fontweight='bold', y=1.02)

        if download:
            plt.savefig(f"{valid_f_paths[0]}/game_record.png", dpi=300, bbox_inches='tight')

        plt.show()


    def _update_best_model(self):
        '''
        update best model to latest model.
        '''
        self.best_model.load_state_dict(self.recent_model.state_dict())
        save_model(self.best_model)
        self.updated = True
        print("Best Model is Updated.")

    def __call__(self, recent_model):
        '''
        this special method starts evaluation.
        '''
        print("")
        print("> Evaluation Started.")
        self._evaluate_network(recent_model)
