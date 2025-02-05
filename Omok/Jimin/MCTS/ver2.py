import sys

# 빌드된 .so 파일 경로 추가
sys.path.append('/Users/ijimin/Documents/GitHub/AiGO/Omok/Jimin/MCTS/build/lib.macosx-11.0-arm64-cpython-312')
import MCTS_cpp

import torch
import random
import numpy as np
from math import sqrt

from main.gameInfo import *


class MCTS:
    def __init__(self, n_playout):
        self.n_playout = n_playout
        self.legal_policy = None
        self.child_n = None

    def get_legal_policy(self, state, model, temp):
        model_4_cpp = torch.jit.script(model)

        def argmax(lst):
            arr = np.array(lst)
            max_indices = np.where(arr == arr.max())[0]
            return int(random.choice(max_indices))

        # define root node
        root_node = MCTS_cpp.Node(state, 0.0)

        # MCTS 시행 ( 트리 확장 과정 )
        for _ in range(self.n_playout):
            root_node.evaluate_value(model_4_cpp._c) # 

        # 자식 노드의 방문 횟수 확인
        childs_n = get_n_child(root_node.child_nodes)

        self.child_n = childs_n
        
        # 원핫 정책
        if temp == 0:
            action = argmax(childs_n)
            legal_policy = np.zeros(len(childs_n))
            legal_policy[action] = 1

        else:
            # by Boltzmann
            legal_policy = self.boltzmann_dist(childs_n, temp)

        return legal_policy

    def get_legal_actions_of(self, model, temp, with_policy=False):
        def get_legal_actions_of(state):
            self.legal_policy = self.get_legal_policy(state, model, temp)
            action = np.random.choice(state.get_legal_actions(), p=self.legal_policy)

            if with_policy:
                # 전체 action에 대한 policy 
                learned_policy = np.zeros([state.n_actions])
                learned_policy[state.get_legal_actions()] = self.legal_policy

                # 전체 action에 대한 visit cnt
                visits_cnt = np.zeros([state.n_actions])
                visits_cnt[state.get_legal_actions()] = self.child_n

                return action, learned_policy, visits_cnt # (action, policy, visits_cnt)
            
            return action
        return get_legal_actions_of

    def boltzmann_dist(self, x_lst, temp):
        x_lst = [x ** (1/temp) for x in x_lst]
        return [x/sum(x_lst) for x in x_lst]
    

def get_n_child(child_nodes):

    child_n = []

    for node in child_nodes:
        child_n.append(node.n)

    return child_n