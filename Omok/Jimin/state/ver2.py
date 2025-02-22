import sys
import os
import copy
import numpy as np
from abc import ABC, abstractmethod

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.config import *

class BaseState(ABC):
    '''
    Structure for State. 
    This abstract class bulids whole state except __call__() which makes state for train.  
    '''
    __slots__ = ('player_state', 'enemy_state', 'next_action', 'state_shape', 
                 'action_space', 'n_actions', 'winning_condition', 'done_condition')
    
    def __init__(self, player_state=None, enemy_state=None, next_action=None, state_shape=STATE_SHAPE):
        # player, enemy's action
        self.player_state = np.zeros(shape=state_shape) if player_state is None else copy.deepcopy(player_state) 
        self.enemy_state = np.zeros(state_shape) if enemy_state is None else copy.deepcopy(enemy_state)
        if next_action is not None:
            np.put(self.enemy_state, next_action, 1) 

        self.next_action = next_action

        # state shape
        self.state_shape = state_shape

        # state info about action space
        self.action_space = range(self.state_shape[0]*self.state_shape[1])
        self.n_actions = len(self.action_space)

        # calculate legal actions
        self.winning_condition = WINNING_CONDITION

        self.done_condition = [None] * 3 # win, draw, lose 

    def next(self, action : int):
        return self.__class__(self.enemy_state, self.player_state, next_action=action)

    def get_legal_actions(self):
        my_actions_set = set(np.where(self.player_state.reshape(-1) != 0)[0])
        enemy_actions_set = set(np.where(self.enemy_state.reshape(-1) != 0)[0])

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

    def _make_diag_mask(self):
        mask = np.zeros(shape=STATE_SHAPE, dtype=bool)
        mask[:, -(self.winning_condition-1):] = 1
        return mask

    def _check_winning_condition(self, board):
        def _get_mask(indices):
            mask = np.zeros(shape=N_ACTIONS)
            mask[indices] = 1
            return mask.astype(bool).reshape(STATE_SHAPE)

        # mask & unavailble idx list 
        diag_mask = self._make_diag_mask()
        anti_diag_mask = diag_mask[:,::-1]

        diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[diag_mask])
        anti_diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[anti_diag_mask])

        # 
        board = board.astype(bool)

        # 조기 종료 
        if np.sum(board) < self.winning_condition:
            return False
        
        # row wise 
        count_five = np.sum(board, axis=1)
        if np.any(count_five >= self.winning_condition):
            is_row = np.any(np.apply_along_axis(lambda x: self._check_row_consecutive(x), axis=1, arr=board))
            if is_row:
                return True

        # col wise
        count_five = np.sum(board, axis=0)
        if np.any(count_five >= self.winning_condition):
            is_col = np.any(np.apply_along_axis(lambda x: self._check_row_consecutive(x), axis=0, arr=board))
            if is_col:
                return True
        
        # 대각 조건이 맞는지 
        indices = np.arange(N_ACTIONS)[board.reshape(-1)] 

        for index in indices:
            if index not in anti_diag_idx_list:
                anti_diag_lst = list(range(index, index+(self.winning_condition-1)*(STATE_SHAPE[1]-1)+1, STATE_SHAPE[1]-1))
                if max(anti_diag_lst) < N_ACTIONS:
                    anti_diag_mask = _get_mask(anti_diag_lst)
                    is_anti_diag = board[anti_diag_mask].all()

                    if is_anti_diag:
                        return True 
                
            if index not in diag_idx_list:
                diag_lst = list(range(index, index+(self.winning_condition-1)*(STATE_SHAPE[1]+1)+1, STATE_SHAPE[1]+1))
                if max(diag_lst) < N_ACTIONS:
                    diag_mask = _get_mask(diag_lst)
                    is_diag = board[diag_mask].all()

                    if is_diag:
                        return True 
                
        return False

    def _check_winning_condition_with_action(self, board):
        if np.sum(board) < self.winning_condition:
            return False
        
        row, col = divmod(self.next_action, STATE_SHAPE[1])

        # 가로 검사
        if self._check_row_consecutive(board[row, :]):
            return True

        # 세로 검사
        if self._check_row_consecutive(board[:, col]):
            return True

        # 정 대각선 (↘) 검사: np.diagonal() 활용
        is_diag = self._check_row_consecutive(np.diagonal(board, offset=col - row))
        if is_diag:
            return True

        # 반대 대각선 (↙) 검사: np.diagonal() 활용 (우상향 대각선)
        flipped_board = np.fliplr(board)  # 보드를 좌우 반전하여 반대 대각선 ↙을 주 대각선 ↘으로 변환
        anti_diag_values = np.diag(flipped_board, k=STATE_SHAPE[1] - 1 - (col + row))

        is_anti_diag = self._check_row_consecutive(anti_diag_values)
        if is_anti_diag:
            return True

        return False

    def is_win(self):
        condition = self._check_winning_condition(self.player_state) 
        self.done_condition[0] = condition
        return condition

    def is_draw(self):
        condition = (np.sum(self.player_state) + np.sum(self.enemy_state)) >= self.n_actions
        self.done_condition[1] = condition
        return condition

    def is_lose(self):
        condition = self._check_winning_condition(self.enemy_state) if self.next_action is None else self._check_winning_condition_with_action(self.enemy_state)
        self.done_condition[2] = condition
        return condition

    def is_done(self):
        if any(self.done_condition):
            return True  

        if self.is_win():
            return True
        if self.is_draw():
            return True
        if self.is_lose():
            return True

        return False
            

    def is_first_player(self):
        return (np.sum(self.player_state) + np.sum(self.enemy_state)) % 2 == 0

    def _render_board_to_str(self):
        
        board = self.player_state + self.enemy_state * -1 if self.is_first_player() else self.player_state * -1 + self.enemy_state
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

    def __str__(self):
        return self._render_board_to_str()
    
    @abstractmethod
    def __call__(self):
        pass

def select_state(n_dim=1):
    class BasicState(BaseState):
        def __call__(self):
            '''
            (2, *STATE_SHAPE)
            [0] : player board 
            [1] : enemy board 
            '''
            return np.stack([self.player_state, self.enemy_state], axis=0)

    class FirstMoveState(BaseState):
        def __call__(self):
            '''
            (3, *STATE_SHAPE)
            [0] : player board 
            [1] : enemy board 
            [2] : 1 is first player? else 0
            '''
            state = np.zeros(shape=(3,*STATE_SHAPE))
            state[0] = self.player_state
            state[1] = self.enemy_state
            if self.is_first_player():
                state[2] = 1
            
            return state 
        
    class ActionAwareState(BaseState):
        def __call__(self):
            '''
            (4, *STATE_SHAPE)
            [0] : player board 
            [1] : enemy board 
            [2] : previous enemy's action as one-hot 
            [3] : 1 is first player? else 0
            '''
            state = np.zeros(shape=(4, *STATE_SHAPE))
            state[0] = self.player_state
            state[1] = self.enemy_state
            if self.next_action is not None:
                row, col = divmod(self.next_action, STATE_SHAPE[1])
                state[2, row, col] = 1
            if self.is_first_player():
                state[3] = 1
            return state
        
    class WithPreviousState(BaseState):
        def __call__(self):
            '''
            (5, *STATE_SHAPE)
            [0] : player board 
            [1] : enemy board 
            [2] : player board before 1 step (fixed)
            [3] : enemy board before 1 step (changed by action)
            [4] : 1 is first player? else 0
            '''
            state = np.zeros(shape=(5, *self.state_shape))
            state[(0, 2), :] = self.player_state
            state[(1, 3), :] = self.enemy_state
            if self.next_action is not None:
                row, col = divmod(self.next_action, self.state_shape[1])
                state[3, row, col] = 0
            if self.is_first_player():
                state[4] = 1
            return state
        
    state_classes = {
        2 : BasicState,
        3 : FirstMoveState, 
        4 : ActionAwareState,
        5 : WithPreviousState
        }
    
    if n_dim not in state_classes:
        raise ValueError(f"Invalid state dimension: {n_dim}. Choose from {list(state_classes.keys())}")
    
    return state_classes[n_dim]