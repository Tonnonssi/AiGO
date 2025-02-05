import torch
import random
import numpy as np
from math import sqrt

from main.gameInfo import *
from main.hyperParams import *


class MCTS:
    def __init__(self, n_playout):
        self.n_playout = n_playout
        self.legal_policy = None
        self.child_n = None

    def get_legal_policy(self, state, model, temp):
        def argmax(lst):
            arr = np.array(lst)
            max_indices = np.where(arr == arr.max())[0]
            return int(random.choice(max_indices))

        # define root node
        root_node = Node(state, 0)

        # MCTS 시행 ( 트리 확장 과정 )
        for _ in range(self.n_playout):
            root_node.evaluate_value(model)

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
            action = np.random.choice(state.legal_actions, p=self.legal_policy)

            if with_policy:
                # 전체 action에 대한 policy 
                learned_policy = np.zeros([state.n_actions])
                learned_policy[state.legal_actions] = self.legal_policy

                # 전체 action에 대한 visit cnt
                visits_cnt = np.zeros([state.n_actions])
                visits_cnt[state.legal_actions] = self.child_n

                return action, learned_policy, visits_cnt # (action, policy, visits_cnt)
            
            return action
        return get_legal_actions_of

    def boltzmann_dist(self, x_lst, temp):
        x_lst = [x ** (1/temp) for x in x_lst]
        return [x/sum(x_lst) for x in x_lst]
    

class Node:
    def __init__(self, state, p):
        self.state = state
        self.p = p # prior prob
        self.n = 0 # n_visit
        self.w = 0 # cum weight
        self.child_nodes = []

    def evaluate_value(self, model):
        if self.state.is_done():
            # judge current value
            value = -1 if self.state.is_lose() else 0 # 패배 혹은 무승부

            # update
            self.n += 1
            self.w += value

            return value

        # When child node does not exist.
        if len(self.child_nodes) == 0:
            legal_policy, value = predict(model, self.state) # by using nn

            # update
            self.n += 1
            self.w += value

            # expand
            for action, p in zip(self.state.legal_actions, legal_policy):
                self.child_nodes.append(Node(self.state.next(action), p))

            return value

        # When child node exist
        else:
            value = - self._select_next_child_node().evaluate_value(model)

            # update
            self.n += 1
            self.w += value

            return value

    def _select_next_child_node(self):
        # PUCT 알고리즘을 사용

        total_visit = sum(get_n_child(self.child_nodes))

        values = []

        for child_node in self.child_nodes:
            q_value = -(child_node.w / child_node.n) if child_node.n != 0 else 0
            node_value = q_value + C_PUCT * child_node.p * sqrt(total_visit) / (1 + child_node.n) # PUCT 알고리즘
            values.append(node_value)

        return self.child_nodes[np.argmax(values)]
    

def get_n_child(child_nodes):

    child_n = []

    for node in child_nodes:
        child_n.append(node.n)

    return child_n


def predict(model, state):
    '''
    predict method returns *legal* policy & value of current state.
    '''
    # device
    device = next(model.parameters()).device

    # ========== 주의해서 봐 =============
    x = torch.tensor(state(), dtype=torch.float32).reshape(1,-1,*STATE_SHAPE) # state.board.shape
    x = x.to(device)

    model.eval()

    with torch.no_grad():
        raw_policy, value = model(x)
        raw_policy, value = raw_policy.detach().cpu().numpy().reshape(-1), float(value.detach())

    # take legal policy

    legal_policy = raw_policy[state.legal_actions]
    legal_policy /= sum(legal_policy) if sum(legal_policy) else 1

    return legal_policy, value