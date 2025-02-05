import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.gameInfo import *

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

    def _check_winning_condition(self, board):
        def _check_row_consecutive(single_arr):
            for i in range(len(single_arr) - self.winning_condition + 1):
                if all(single_arr[i:i+self.winning_condition]):    
                    return True
            return False
        
        board = board.astype(bool)

        is_row = np.any(np.apply_along_axis(lambda x: _check_row_consecutive(x), axis=1, arr=board))

        if is_row:
            return True
        
        # 세로, 대각 조건이 맞는지 
        indices = np.arange(N_ACTIONS)[board.reshape(-1)] 

        for index in indices:
            if index not in self.anti_diag_idx_list:
                anti_diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]-1)+1, STATE_SHAPE[1]-1))
                is_anti_diag = all(element in indices for element in anti_diag_lst)

                if is_anti_diag:
                    return True 
                
            if index not in self.diag_idx_list:
                diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]+1)+1, STATE_SHAPE[1]+1))
                is_diag = all(element in indices for element in diag_lst)

                if is_diag:
                    return True 
                
            
            col_lst = list(range(index, index+(WINNING_CONDITION-1)*STATE_SHAPE[1]+1, STATE_SHAPE[1]))
            is_col = all(element in indices for element in col_lst)

            if is_col:
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
        condition = self._check_winning_condition(enemy_state)
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
