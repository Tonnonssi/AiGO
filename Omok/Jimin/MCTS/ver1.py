import torch
import numpy as np
from math import sqrt


class MCTS:
    def __init__(self, evaluate_count):
        self.evaluate_count = evaluate_count
        self.legal_policy = None

    def get_legal_policy(self, state, model, temp):
        # define root node
        root_node = Node(state, 0)

        for _ in range(self.evaluate_count):
            root_node.evaluate_value(model)

        # 자식 노드의 방문 횟수 확인
        childs_n = get_n_child(root_node.child_nodes)

        # 원핫 정책
        if temp == 0:
            action = np.argmax(childs_n)
            legal_policy = np.zeros(len(childs_n))
            legal_policy[action] = 1

        else:
            # by Boltzmann
            legal_policy = self.boltzmann_dist(childs_n, temp)

        return legal_policy

    def get_legal_actions_of(self, model, temp):
        def get_legal_actions_of(state):
            self.legal_policy = self.get_legal_policy(state, model, temp)
            action = np.random.choice(state.legal_actions, p=self.legal_policy)
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
            value = - self.select_next_child_node().evaluate_value(model)

            # update
            self.n += 1
            self.w += value

            return value

    def select_next_child_node(self):
        # PUCT 알고리즘을 사용

        C_PUCT = 1.0 # 탐험의 정도

        total_visit = sum(get_n_child(self.child_nodes))

        values = []

        for node in self.child_nodes:
            q_value = -(node.w / node.n) if node.n != 0 else 0
            node_value = q_value + C_PUCT * node.p * sqrt(total_visit) / (1 + node.n) # PUCT 알고리즘
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

    x = torch.tensor(state.board, dtype=torch.float32).reshape(1,*state.board.shape)
    x = x.to(device)

    model.eval()

    with torch.no_grad():
        raw_policy, value = model(x)
        raw_policy, value = raw_policy.detach().cpu().numpy().reshape(-1), float(value.detach())

    # take legal policy

    legal_policy = raw_policy[state.legal_actions]
    legal_policy /= sum(legal_policy) if sum(legal_policy) else 1

    return legal_policy, value