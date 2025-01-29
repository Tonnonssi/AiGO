import torch
import matplotlib.pyplot as plt

from MCTS.ver1 import *
from state.ver2 import *
from visualize.valid_tool import *
from utils.saveLoad import *

class EvalNetwork:
    def __init__(self, best_model, eval_game_count, eval_temperature, eval_count):
        # eval info
        self.eval_game_count = eval_game_count
        self.eval_temperature = eval_temperature

        # models
        self.best_model = best_model
        self.recent_model = None

        # MCTS
        self.mcts = MCTS(eval_count)

        # init value
        self.updated = False
        self.win_rate = 0.0

        # for visualize result
        # recent model 시점의 승패 결과다. 
        self.game_result = {'lose' : 0,
                            'draw' : 0,
                            'win' : 0}

    def _first_player_point(self, ended_state):
        # 1: 선 수 플레이어 승리, 0: 선 수 플레이어 패배, 0.5: 무승부
        if ended_state.is_lose():
            return 0 if ended_state.is_first_player() else 1
        return 0.5

    def _evaluate_network(self, recent_model):
        # get network
        self.recent_model = recent_model

        # MCTS를 이용
        next_actions_recent = self.mcts.get_legal_actions_of(self.recent_model, 0)
        next_actions_best = self.mcts.get_legal_actions_of(self.best_model, 0)
        next_actions = (next_actions_recent, next_actions_best)

        total_point = 0

        for i in range(self.eval_game_count):
            if i % 2 == 0: # 최근 모델이 선
                point = self._single_play(next_actions)
                self.game_result[list(self.game_result.keys())[int(point*2)]] += 1
                total_point += point

            else: # 베스트 모델이 선 
                point = 1 - self._single_play(list(reversed(next_actions)))
                self.game_result[list(self.game_result.keys())[int(point*2)]] += 1
                total_point += point

        average_point = total_point / self.eval_game_count

        print('Average Point of Latest Model', average_point)

        visualize_game_result(self.game_result) # visualize circle graph 

        if average_point >= 0.5:
            self._update_best_model()

        self.win_rate = (round(self.game_result['win'] / sum(self.game_result.values()), 2), round(self.game_result['win'] + self.game_result['draw'] / sum(self.game_result.values()), 2)
)
    def _single_play(self, next_actions):

        state = State()

        while True:
            if state.is_done():
                break

            get_next_action = next_actions[0] if state.is_first_player() else next_actions[1]

            action = get_next_action(state)
            state = state.next(action)

        return self._first_player_point(state)
    
    def _visualize_game_step(self, next_actions:list, first_agent_type='recent', path=None, download=False):

        total_game_steps = []
        type_label = ['best', 'recent'] if first_agent_type == 'recent' else ['recent', 'best']

        state = State()

        for step in range(N_ACTIONS):
            if state.is_done():
                return total_game_steps

            get_next_action_policy_nvisits = next_actions[0] if state.is_first_player() else next_actions[1]
            first_agent_type = type_label[int(state.is_first_player())]
            
            action, policy, n_visits = get_next_action_policy_nvisits(state)
            visualize_pack(first_agent_type, state(), n_visits, policy, action, step, path, download)

            total_game_steps.append(action)
            state = state.next(action)

    def visualize_game(self, idx=0, recent_model=None, download=False):
        # get network
        self.recent_model = recent_model if recent_model is not None else self.recent_model

        # 시각화 내용을 저장할 폴더 생성 
        # (valid_f_path, valid_recent_f_path, valid_best_f_path)
        valid_f_paths = make_valid_file_paths(idx) if download else None 

        # MCTS를 이용
        next_actions_recent = self.mcts.get_legal_actions_of(self.recent_model, 0, with_policy=True)
        next_actions_best = self.mcts.get_legal_actions_of(self.best_model, 0, with_policy=True)
        next_actions_list = (next_actions_recent, next_actions_best)
        
        # step마다 시각화 & 기보 시각화를 위한 action list return 
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
        self.best_model.load_state_dict(self.recent_model.state_dict())

        self.updated = True
        print("Best Model is Updated.")

    def __call__(self, recent_model):
        self._evaluate_network(recent_model)
