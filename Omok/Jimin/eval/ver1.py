import torch
from MCTS.ver1 import *
from state.ver1 import *

class EvalNetwork:
    def __init__(self, best_model, eval_game_count, eval_temperature, eval_count, path, name):
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

        self.name = name
        self.path = path

    def _first_player_point(self, ended_state):
        # 1: 선 수 플레이어 승리, 0: 선 수 플레이어 패배, 0.5: 무승부
        if ended_state.is_lose():
            return 0 if ended_state.is_first_player() else 1
        return 0.5

    def _evaluate_network(self, recent_model):
        # get network
        self.recent_model = recent_model

        # MCTS를 이용
        next_actions_recent = self.mcts.get_legal_actions_of(self.recent_model, self.eval_temperature)
        next_actions_best = self.mcts.get_legal_actions_of(self.best_model, self.eval_temperature)
        next_actions = (next_actions_recent, next_actions_best)

        total_point = 0

        for i in range(self.eval_game_count):
            if i % 2 == 0:
                total_point += self._single_play(next_actions)
            else:
                total_point += 1 - self._single_play(list(reversed(next_actions)))

        average_point = total_point / self.eval_game_count

        print('Average Point of Latest Model', average_point)

        if average_point >= 0.5:
            self._update_best_model()

    def _single_play(self, next_actions):

        state = State()

        while True:
            if state.is_done():
                break

            next_action = next_actions[0] if state.is_first_player() else next_actions[1]

            action = next_action(state)
            state = state.next(action)

        return self._first_player_point(state)

    def _update_best_model(self):
        self.best_model.load_state_dict(self.recent_model.state_dict())

        self.updated = True
        print("Best Model is Updated.")

    def save_model(self):
        
        path = f'{self.path}/{self.name}'

        # 디렉토리 생성
        if not os.path.exists(path):
            os.makedirs(path)  

        torch.save(self.best_model.state_dict(), f'{path}/best_model_weight.pth')

    def __call__(self, recent_model):
        self._evaluate_network(recent_model)