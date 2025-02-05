import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.gameInfo import *

class State:
    def __init__(self, my_actions=None, enemy_actions=None, next_action=None, state_shape=STATE_SHAPE):
        # mine, enemy's action
        self.my_actions = [] if my_actions is None else my_actions 
        self.enemy_actions = [] if enemy_actions is None else enemy_actions if next_action is None else enemy_actions + [next_action]
        self.next_action = next_action

        # state shape
        self.state_shape = state_shape

        # state info about action space
        self.action_space = range(self.state_shape[0]*self.state_shape[1])
        self.n_actions = len(self.action_space)

        # create board
        self.board = self._create_board(self.my_actions, self.enemy_actions)

        # calculate legal actions
        self.legal_actions = self._get_legal_actions()
        self.winning_condition = WINNING_CONDITION

        self.done_condition = [None] * 3 # win, draw, lose 

        # mask & unavailble idx list 
        self.diag_mask = self._make_diag_mask()
        self.anti_diag_mask = self.diag_mask[:,::-1]

        self.diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[self.diag_mask])
        self.anti_diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[self.anti_diag_mask])

    def _make_diag_mask(self):
        mask = np.zeros(shape=STATE_SHAPE, dtype=bool)
        mask[:, -(WINNING_CONDITION-1):] = 1
        return mask

    def next(self, action):
        return State(self.enemy_actions, self.my_actions, next_action=action)

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

    def _check_row_consecutive(self, single_arr):
        if np.sum(single_arr) < self.winning_condition:
            return False

        if (len(single_arr) == self.winning_condition) & (np.sum(single_arr) == self.winning_condition):
            return True

        for i in range(len(single_arr) - self.winning_condition + 1):
            if all(single_arr[i:i+self.winning_condition]):    
                return True
        return False

    def _check_winning_condition(self, board):
        def _get_mask(indices):
            mask = np.zeros(shape=N_ACTIONS)
            mask[indices] = 1
            return mask.astype(bool).reshape(STATE_SHAPE)
        
        board = board.astype(bool)

        # 조기 종료 
        if np.sum(board) < self.winning_condition:
            return False
        
        # row wise 
        count_five = np.sum(board, axis=1)
        if np.any(count_five >= WINNING_CONDITION):
            is_row = np.any(np.apply_along_axis(lambda x: self._check_row_consecutive(x), axis=1, arr=board))
            if is_row:
                return True

        # col wise
        count_five = np.sum(board, axis=0)
        if np.any(count_five >= WINNING_CONDITION):
            is_col = np.any(np.apply_along_axis(lambda x: self._check_row_consecutive(x), axis=0, arr=board))
            if is_col:
                return True
        
        # 대각 조건이 맞는지 
        indices = np.arange(N_ACTIONS)[board.reshape(-1)] 

        for index in indices:
            if index not in self.anti_diag_idx_list:
                anti_diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]-1)+1, STATE_SHAPE[1]-1))
                if max(anti_diag_lst) < N_ACTIONS:
                    anti_diag_mask = _get_mask(anti_diag_lst)
                    is_anti_diag = board[anti_diag_mask].all()

                    if is_anti_diag:
                        return True 
                
            if index not in self.diag_idx_list:
                diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]+1)+1, STATE_SHAPE[1]+1))
                if max(diag_lst) < N_ACTIONS:
                    diag_mask = _get_mask(diag_lst)
                    is_diag = board[diag_mask].all()

                    if is_diag:
                        return True 
                
        return False

    def _check_winning_condition_with_action(self, board):
        # 조기 종료 
        if np.sum(board) < self.winning_condition:
            return False
        
        row, col = divmod(self.next_action, STATE_SHAPE[1])

        # check row
        is_row = self._check_row_consecutive(board[row, :])
        if is_row:
            return True

        # check col
        is_col = self._check_row_consecutive(board[:, col])
        if is_col:
            return True

        # check diagonal ↘ (main diagonal)
        diag_start_row = max(row - col, 0)  # 시작 행
        diag_start_col = max(col - row, 0)  # 시작 열
        diag_values = np.diag(board, k=diag_start_col - diag_start_row)  # 주 대각선 추출

        is_diag = self._check_row_consecutive(diag_values)
        if is_diag:
            return True

        # check anti-diagonal ↙ (secondary diagonal)
        flipped_board = np.fliplr(board)  # 보드를 좌우 반전하여 반대 대각선 ↙을 주 대각선 ↘으로 변환
        anti_diag_values = np.diag(flipped_board, k=STATE_SHAPE[1] - 1 - (col + row))

        is_anti_diag = self._check_row_consecutive(anti_diag_values)
        if is_anti_diag:
            return True

        return False

    def is_win(self):
        my_state = self.board[0]
        condition = self._check_winning_condition(my_state) 
        self.done_condition[0] = condition
        return condition

    def is_draw(self):
        condition = (np.sum(self.board[0]) + np.sum(self.board[1])) >= self.n_actions
        self.done_condition[1] = condition
        return condition

    def is_lose(self):
        enemy_state = self.board[1]
        condition = self._check_winning_condition(enemy_state) if self.next_action is None else self._check_winning_condition_with_action(enemy_state)
        self.done_condition[2] = condition
        return condition

    def is_done(self):
        if None in self.done_condition:
            return self.is_win() or self.is_draw() or self.is_lose()
        else:
            return any(self.done_condition)
            

    def is_first_player(self):
        return (len(self.my_actions) + len(self.enemy_actions)) % 2 == 0

    def _render_board_to_str(self):
        
        board = self.board[0] + self.board[1] * -1 if self.is_first_player() else self.board[0] * -1 + self.board[1]
        mapping = {0: '.', 1: '●', -1 : '○'}

        # Create column legend (header)
        col_legend = '  ' + ' '.join(map(str, range(board.shape[1])))

        # Create rows with row legend (A, B, C, ...)
        row_legend = []

        for i, row in enumerate(board):
            row_label = chr(65 + i)  # Convert row index to A, B, C, ...
            row_str = ' '.join(mapping[val] for val in row)
            row_legend.append(f"{row_label} {row_str}")

        # Combine the column legend and rows
        return '\n'.join([col_legend] + row_legend)
    
    def __call__(self):
        return self.board[:2]

    def __str__(self):
        return self._render_board_to_str()
    

if __name__=="__main__":
    s = State(list(range(23, 56, 8)),[1,2,3,4])
    print(s)
    print()
    print(f"is first player? : {s.is_first_player()}")
    print(f"is win : {s.is_win()}")
    print(f"is draw : {s.is_draw()}")
    print(f"is lose : {s.is_lose()}")
    print(f"is done : {s.is_done()}")
