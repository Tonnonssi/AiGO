from Omok.Jimin.MCTS.ver1 import *
from web.models.load_model import *

# define 
mcts = MCTS(N_PLAYOUT)

# 
get_next_action = mcts.get_legal_actions_of(model, 0, with_policy=False)
