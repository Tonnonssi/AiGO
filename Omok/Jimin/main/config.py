import os

# game info # 
STATE_SHAPE = (9,9) 
N_ACTIONS = STATE_SHAPE[0]*STATE_SHAPE[1]
WINNING_CONDITION = 5

# file setting #
D_NAME = 'model'
F_NAME = 'Omok_3'
F_CWD = os.path.abspath(os.path.join(os.getcwd(), ".."))
F_PATH = f"{F_CWD}/{D_NAME}/{F_NAME}"

# state info #
STATE_DIM = 4 # (2,3,4,5)

# count #
TOTAL_SELFPLAY = 2000
EVAL_SELFPLAY = 20  
N_PLAYOUT = 400
TRAIN_EPOCHS = 10
MEM_SIZE = 30000

# nn #
N_KERNEL = 128
N_RESIDUAL_BLOCK = 10
BATCH_SIZE = 512 

# learning rate #
LEARNING_RATE = 2e-4
LEARN_DECAY = 1.0

L2 = 1e-4

# temperture : Boltzman #
TRAIN_TEMPERATURE = 1.0 
EVAL_TEMPERATURE = 0 

# selfplay : exploration #
C_PUCT = 5.0
EXPLORE_REGULATION = 10 # (None or int) 

# frequency # 
TRAIN_FREQUENCY = 1
EVAL_FREQUENCY = 50
VISUALIZATION_FREQUENCY = 200
LEARN_FREQUENCY = 1000

total_iter = TOTAL_SELFPLAY //TRAIN_FREQUENCY
eval_index = EVAL_FREQUENCY // TRAIN_FREQUENCY
visualization_index = VISUALIZATION_FREQUENCY // TRAIN_FREQUENCY
learn_decay_index = LEARN_FREQUENCY // TRAIN_FREQUENCY


config = f'''
# game info # 
STATE_SHAPE = {STATE_SHAPE} 
N_ACTIONS = {N_ACTIONS}
WINNING_CONDITION = {WINNING_CONDITION}

# state info #
STATE_DIM = {STATE_DIM}

# count #
TOTAL_SELFPLAY = {TOTAL_SELFPLAY}
EVAL_SELFPLAY = {EVAL_SELFPLAY}  
N_PLAYOUT = {N_PLAYOUT} 
TRAIN_EPOCHS = {TRAIN_EPOCHS}
MEM_SIZE = {MEM_SIZE}

# nn #
N_KERNEL = {N_KERNEL}
N_RESIDUAL_BLOCK = {N_RESIDUAL_BLOCK}
BATCH_SIZE = {BATCH_SIZE}

# learning rate #
LEARNING_RATE = {LEARNING_RATE}
LEARN_DECAY = {LEARN_DECAY}

L2 = {L2}

# temperture : Boltzman #
TRAIN_TEMPERATURE = {TRAIN_TEMPERATURE}
EVAL_TEMPERATURE = {EVAL_TEMPERATURE} 

# selfplay : exploration #
C_PUCT = {C_PUCT}
EXPLORE_REGULATION = {EXPLORE_REGULATION}

# frequency # 
TRAIN_FREQUENCY = {TRAIN_FREQUENCY}
EVAL_FREQUENCY = {EVAL_FREQUENCY}
VISUALIZATION_FREQUENCY = {VISUALIZATION_FREQUENCY}
LEARN_FREQUENCY = {LEARN_FREQUENCY}

'''