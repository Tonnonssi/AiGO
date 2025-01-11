STATE_SHAPE = (3, 3)
N_ACTIONS = STATE_SHAPE[0]*STATE_SHAPE[1]
STATE_DIM = 3 # ( my_actions, enemy_actions, first player ) 
BOARD_SHAPE = (STATE_DIM, *STATE_SHAPE)