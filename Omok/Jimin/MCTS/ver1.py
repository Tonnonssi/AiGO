import torch
import random
import numpy as np
from math import sqrt

from Omok.Jimin.main.config import *
from Omok.Jimin.utils.transpose_state import *


class MCTS:
    '''
    MCTS(n_playout : int)

    The MCTS class performs Monte Carlo Tree Search (MCTS) simulations to derive the policy for the current state.
    The parameter n_playout defines the number of simulations used to generate a single policy.
    '''
    def __init__(self, n_playout):
        self.n_playout = n_playout
        self.legal_policy = None
        self.child_n = []

    def get_legal_policy(self, state, model, temp):
        '''
        get_legal_policy(state : class, model : nn.Module, temp : float) -> legal_policy : list[float]

        This method gets legal policy by using MCTS. 
        Legal policy is based on child nodes' visit cnt and normally composed by Boltzmann distribution. 
        Sepically when temp == 0, the legal policy will be formed as one-hot encoded vector.
        '''

        # define root node
        root_node = Node(state, 1.0)

        # launch MCTS == expansion of Tree 
        for _ in range(self.n_playout):
            root_node.evaluate_value(model)

        # check child nodes' visit cnt
        childs_n = get_n_child(root_node.child_nodes)

        self.child_n = childs_n
        
        # one-hot
        if temp == 0:
            action = argmax(childs_n)
            legal_policy = np.zeros(len(childs_n))
            legal_policy[action] = 1

        else:
            # by Boltzmann
            legal_policy = self.boltzmann_dist(childs_n, temp)

        return legal_policy

    def get_legal_actions_of(self, model, temp, with_policy=False):
        '''
         get_legal_actions_of(model, temp, with_policy=False) ->  get_legal_actions_of : method

         This method returns method set by init params. 
        '''
        def get_legal_action_of(state):
            '''
            get_legal_actions_of(state : class) -> action : int 

            This method get legal action. 
            '''
            self.legal_policy = self.get_legal_policy(state, model, temp)
            action = np.random.choice(state.get_legal_actions(), p=self.legal_policy)

            return action
        
        def get_action_with_visualize_pkg_of(state):
            '''
            get_legal_actions_of(state : class) -> action, learned_policy, visits_cnt

            This method gets legal action-policy-visit cnt for visualization. 
            return values are based on *whole action space*.
            '''
            self.legal_policy = self.get_legal_policy(state, model, temp)
            action = np.random.choice(state.get_legal_actions(), p=self.legal_policy)

            learned_policy = np.zeros([state.n_actions])
            learned_policy[state.get_legal_actions()] = self.legal_policy

            visits_cnt = np.zeros([state.n_actions])
            visits_cnt[state.get_legal_actions()] = self.child_n

            return action, learned_policy, visits_cnt 
        

        return get_action_with_visualize_pkg_of if with_policy else get_legal_action_of

    def boltzmann_dist(self, n_lst, temp):
        '''
        boltzmann_dist(n_lst : list, temp : float) -> list[float]

        temp = (0,1]
        n_lst : list of cnt 
        
        This method converts visits num of child nodes to policy.
        '''
        n_lst = [n ** (1/temp) for n in n_lst]
        return [n/sum(n_lst) for n in n_lst]
    

class Node:
    __slots__ = ('state', 'p', 'n', 'w', 'child_nodes')
    '''
    Node(state : class, p : float)

    The Node class is used in the MCTS class to perform Monte Carlo Tree Search(MCTS). 

    : main method : 
    evaluate_value(model) -> value

    '''
    def __init__(self, state, p):
        self.state = state
        self.p = p # prior prob
        self.n = 0 # n_visit
        self.w = 0 # cum weight
        self.child_nodes = []

    def evaluate_value(self, model):
        '''
        evaluate_value(model : nn.Module) -> value : float 

        This method evaluates the value of the current node using MCTS.
        The basic process involves traversing to a terminal node to obtain the game result.
        If the current node is non-terminal and has no child nodes, 
        the neural network predicts the legal policy and value, serving as a replacement for rollout.
        '''
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
            for action, p in zip(self.state.get_legal_actions(), legal_policy):
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
        '''
        _select_next_child_node() -> child_node : Node

        This method selects next child node by using PUCT algorithms.
        '''
        total_visit = sum(get_n_child(self.child_nodes))

        values = []

        for child_node in self.child_nodes:
             # PUCT 
            q_value = -(child_node.w / child_node.n) if child_node.n != 0 else 0
            node_value = q_value + C_PUCT * child_node.p * sqrt(total_visit) / (1 + child_node.n)
            values.append(node_value)

        return self.child_nodes[argmax(values)]

def argmax(lst : list):
    '''
    argmax(lst : list)

    This method counts for multiple max value indices which np.argmax() cannot handle.
    '''
    arr = np.array(lst)
    max_indices = np.where(arr == arr.max())[0]
    return int(random.choice(max_indices)) 

def get_n_child(child_nodes : list):
    '''
    get_n_child(child_nodes : list[Node]) -> child_n : list

    This method gets cnt of total child nodes.
    '''
    child_n = []

    for node in child_nodes:
        child_n.append(node.n)

    return child_n


def predict(model, state):
    '''
    predict(model : nn.Module, state : class) -> legal_policy : list[float], value : float

    This method returns *legal* policy & value of current state.
    '''
    # device
    device = next(model.parameters()).device

    # reshape & put on device 
    if ALLOW_TRANSPOSE:
        idx = random.choice(range(8))
        rotate_ftn, revert_ftn = get_dihedral_transpose_ftns(idx)
        rotated_state = rotate_ftn(state()).copy()
        x = torch.tensor(rotated_state, dtype=torch.float32, device=device).reshape(1,-1,*STATE_SHAPE) 

        model.eval()

        with torch.no_grad():
            raw_policy, value = model(x)
            raw_policy, value = raw_policy.detach().cpu().numpy().reshape(-1,*STATE_SHAPE), float(value.detach())
            reverted_raw_policy = revert_ftn(raw_policy).reshape(-1)

        # get legal policy
        legal_policy = reverted_raw_policy[state.get_legal_actions()]
        
    else:
        x = torch.tensor(state(), dtype=torch.float32, device=device).reshape(1,-1,*STATE_SHAPE) 

        model.eval()

        with torch.no_grad():
            raw_policy, value = model(x)
            raw_policy, value = raw_policy.detach().cpu().numpy().reshape(-1), float(value.detach())

        # get legal policy
        legal_policy = raw_policy[state.get_legal_actions()]
        # legal_policy /= sum(legal_policy) if sum(legal_policy) else 1

    return legal_policy, value

