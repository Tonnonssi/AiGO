STATE_SHAPE = (9,9) # 9,9
N_ACTIONS = STATE_SHAPE[0]*STATE_SHAPE[1]
STATE_DIM = 3 # ( my_actions, enemy_actions, first player ) 
BOARD_SHAPE = (STATE_DIM, *STATE_SHAPE)
WINNING_CONDITION = 5

# 게임보드 파라미터 명칭 수정 
