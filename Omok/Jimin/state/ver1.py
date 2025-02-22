import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.config  import *

class State:
    def __init__(self, my_actions=None, enemy_actions=None, state_shape=STATE_SHAPE):
        # mine, enemy's action
        self.my_actions = [] if my_actions is None else my_actions
        self.enemy_actions = [] if enemy_actions is None else enemy_actions

        self.state_shape = state_shape

        # state info about action space
        self.action_space = range(self.state_shape[0]*self.state_shape[1])
        self.n_actions = len(self.action_space)

        # create board
        self.board = self._create_board(self.my_actions, self.enemy_actions)

        # calculate legal actions
        self.legal_actions = self._get_legal_actions()
        self.wining_condition = 3

    def next(self, action):
        my_actions = self.my_actions.copy()
        my_actions.append(action)
        return State(self.enemy_actions, my_actions)

    def _create_board(self, my_actions, enemy_actions):
        # 전체 state
        total_board = np.zeros(shape=(STATE_DIM, *self.state_shape))

        # 내 말과 상대방 말이 놓인 보드를 원핫인코딩으로 표현
        my_board, enemy_board = np.zeros(self.n_actions), np.zeros(self.n_actions)

        my_board[my_actions] = 1
        enemy_board[enemy_actions] = 1

        total_board[0] = my_board.reshape(self.state_shape)
        total_board[1] = enemy_board.reshape(self.state_shape)
        total_board[2] = np.full(self.state_shape, fill_value=1) if not self.is_first_player() else np.zeros(self.state_shape)

        return total_board

    def _get_legal_actions(self):
        my_actions_set = set(self.my_actions)
        enemy_actions_set = set(self.enemy_actions)

        return list(set(self.action_space) - my_actions_set - enemy_actions_set)

    def is_win(self):
        my_state = self.board[0]

        rows_win = (my_state == 1).sum(axis=0).max() == self.wining_condition
        cols_win = (my_state == 1).sum(axis=1).max() == self.wining_condition
        diag_win = np.diag(my_state).sum() == self.wining_condition
        anti_diag_win = np.diag(np.fliplr(my_state)).sum() == self.wining_condition

        return rows_win or cols_win or diag_win or anti_diag_win

    def is_draw(self):
        return (np.sum(self.board[0]) + np.sum(self.board[1])) >= self.n_actions

    def is_lose(self):
        enemy_state = self.board[1]

        rows_lose = (enemy_state == 1).sum(axis=0).max() == self.wining_condition
        cols_lose = (enemy_state == 1).sum(axis=1).max() == self.wining_condition
        diag_lose = np.diag(enemy_state).sum() == self.wining_condition
        anti_diag_lose = np.diag(np.fliplr(enemy_state)).sum() == self.wining_condition

        return rows_lose or cols_lose or diag_lose or anti_diag_lose

    def is_done(self):
        return self.is_win() or self.is_draw() or self.is_lose()

    def is_first_player(self):
        return len(self.my_actions) == len(self.enemy_actions)
    

if __name__=="__main__":
    s = State([0,1],[3])
    print(s.board)