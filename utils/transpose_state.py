import numpy as np

def rotate_90(board):
    '''
    90 degree 시계 방향 회전 
    '''
    return np.rot90(board, k=-1, axes=(1, 2)) 

def rotate_180(board):
    '''
    180 degree 시계 방향 회전 
    '''
    return np.rot90(board, k=-2, axes=(1, 2)) 

def rotate_270(board):
    '''
    270 degree 시계 방향 회전 
    '''
    return np.rot90(board, k=-3, axes=(1, 2)) 

def flip_vertical(board):
    '''
    상하 반사  
    '''
    return np.flip(board, axis=1)  

def flip_horizontal(board):
    '''
    좌우 반사
    '''
    return np.flip(board, axis=2) 

def flip_diagonal_main(board):
    '''
    주대각선 반사 
    '''
    return np.transpose(board, axes=(0, 2, 1)) 

def flip_diagonal_anti(board):
    '''
    반대 대각선 반사 
    '''
    return np.flip(np.transpose(board, axes=(0, 2, 1)), axis=2) 

# inverse methods 

def inverse_rotate_90(board):
    ''' 
    90도 시계 방향 회전의 역변환 → 90도 반시계 방향 회전 
    '''
    return np.rot90(board, k=1, axes=(1, 2)) 

def inverse_rotate_180(board):
    ''' 
    180도 시계 방향 회전의 역변환 → 180도 회전 (같은 연산) 
    '''
    return np.rot90(board, k=2, axes=(1, 2)) 

def inverse_rotate_270(board):
    ''' 
    270도 시계 방향 회전의 역변환 → 270도 반시계 방향 회전 
    '''
    return np.rot90(board, k=3, axes=(1, 2)) 

def inverse_flip_vertical(board):
    ''' 
    상하 반사의 역변환 → 다시 상하 반사 적용 
    '''
    return np.flip(board, axis=1)

def inverse_flip_horizontal(board):
    ''' 
    좌우 반사의 역변환 → 다시 좌우 반사 적용 
    '''
    return np.flip(board, axis=2)

def inverse_flip_diagonal_main(board):
    ''' 
    주대각선(\\) 반사의 역변환 → 다시 동일한 변환 적용 
    '''
    return np.transpose(board, axes=(0, 2, 1))

def inverse_flip_diagonal_anti(board):
    ''' 
    반대 대각선(/) 반사의 역변환 → 다시 동일한 변환 후 좌우 반사 적용 
    '''
    return np.flip(np.transpose(board, axes=(0, 2, 1)), axis=2)

def get_original(board):
    return board

def get_batched_states(state):
    stacked_state = np.stack([state,
                              rotate_90(state),
                              rotate_180(state),
                              rotate_270(state),
                              flip_horizontal(state),
                              flip_vertical(state),
                              flip_diagonal_main(state),
                              flip_diagonal_anti(state)],
                              axis=0)
    return stacked_state

def get_dihedral_transpose_ftns(idx : int):
    '''
    get_dihedral_transpose_ftns(idx : int) -> [ftn(state), inverse_ftn(policy)]
    state.shape : (-1, *STATE_SHAPE)
    '''
    if idx == 0:
        return [get_original, get_original]
    
    elif idx == 1:
        return [rotate_90, inverse_rotate_90]
    
    elif idx == 2:
        return [rotate_180, inverse_rotate_180]
    
    elif idx == 3:
        return [rotate_270, inverse_rotate_270]
    
    elif idx == 4:
        return [flip_vertical, inverse_flip_vertical]
    
    elif idx == 5:
        return [flip_horizontal, inverse_flip_horizontal]
    
    elif idx == 6:
        return [flip_diagonal_main, inverse_flip_diagonal_main]
    
    elif idx == 7:
        return [flip_diagonal_anti, inverse_flip_diagonal_anti]
    
rotate_ftns = [rotate_90, rotate_180, rotate_270, 
               flip_vertical, flip_horizontal, 
               flip_diagonal_main, flip_diagonal_anti]

