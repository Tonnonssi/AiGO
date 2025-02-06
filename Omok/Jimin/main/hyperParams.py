# game info # 
EPOCHS = 100
STATE_DIM = 4 # 2,3,4,5

# nn #
N_KERNEL = 128
N_RESIDUAL_BLOCK = 16
BATCH_SIZE = 256 # 128

# learning rate #
LEARNING_RATE = 2e-3
LEARN_DECAY = 0.5
LEARN_EPOCH = 50

# Temperture : Boltzman #
TEMP_DISCOUNT = 0.9995
TRAIN_TEMPERATURE = 1.0  # 볼츠만 분포의 온도 파라미터 
EVAL_TEMPERATURE = 1.0  # 볼츠만 분포 온도 파라미터 

# selfplay #
TRAIN_N_SELFPLAY = 20 # 500 # 500
N_PLAYOUT = 200 # 정책을 구할 때 시뮬레이션 횟수 (오리지널 : 1600)
EVAL_GAME_COUNT = 20  # 평가 1회 당 게임 수(오리지널: 400)

# exploration #
C_PUCT = 5.0

hyper_params = f'''
# game info 
EPOCHS = {EPOCHS}
STATE_DIM = {STATE_DIM}

# nn #
N_KERNEL = {N_KERNEL}
N_RESIDUAL_BLOCK = {N_RESIDUAL_BLOCK}
BATCH_SIZE = {BATCH_SIZE} 

# learning rate #
LEARNING_RATE = {LEARNING_RATE}
LEARN_DECAY = {LEARN_DECAY}
LEARN_EPOCH = {LEARN_EPOCH}

# Temperture : Boltzman #
TEMP_DISCOUNT = {TEMP_DISCOUNT}
TRAIN_TEMPERATURE = {TRAIN_TEMPERATURE}  # 볼츠만 분포의 온도 파라미터 
EVAL_TEMPERATURE = {EVAL_TEMPERATURE}  # 볼츠만 분포 온도 파라미터 

# selfplay #
TRAIN_N_SELFPLAY = {TRAIN_N_SELFPLAY} # 500
N_PLAYOUT = {N_PLAYOUT} # 정책을 구할 때 시뮬레이션 횟수 (오리지널 : 1600)
EVAL_GAME_COUNT = {EVAL_GAME_COUNT}  # 평가 1회 당 게임 수(오리지널: 400)

# exploration #
C_PUCT = {C_PUCT}
'''