import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import numpy as np
import copy

from state.ver2 import *
from main.gameInfo import *

def is_first_player(state):
        n_my_actions = np.sum(state[0])
        n_enemy_actions = np.sum(state[1])
        return (n_my_actions + n_enemy_actions) % 2 == 0  

def divide(x):
    row, col = divmod(x, STATE_SHAPE[1])
    row , col = row + 0.5, col + 0.5
    return (row, col)

def check_consecutive(input):
    def _make_diag_mask():
        mask = np.zeros(shape=STATE_SHAPE, dtype=bool)
        mask[:, -(WINNING_CONDITION-1):] = 1
        return mask
    
    if type(input) == np.ndarray:
        indices = np.arange(N_ACTIONS)[input.astype(bool).reshape(-1)] 
    
    elif type(input) == list:
        indices = input
    
    # mask & unavailble idx list 
    diag_mask = _make_diag_mask()
    anti_diag_mask = diag_mask[:,::-1]

    diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[diag_mask])
    anti_diag_idx_list = list(np.arange(N_ACTIONS).reshape(STATE_SHAPE)[anti_diag_mask])           

    for index in indices:
        # find diag & row-consecutive list  
        if index not in diag_idx_list:
                diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]+1)+1, STATE_SHAPE[1]+1))
                row_lst = list(range(index, index+WINNING_CONDITION))

                is_row = all(element in indices for element in row_lst)
                is_diag = all(element in indices for element in diag_lst)

                if is_diag:
                    return True, diag_lst
                elif is_row:
                    return True, row_lst
                
        # find anti-diag-consecutive list  
        if index not in anti_diag_idx_list:
                anti_diag_lst = list(range(index, index+(WINNING_CONDITION-1)*(STATE_SHAPE[1]-1)+1, STATE_SHAPE[1]-1))
                is_anti_diag = all(element in indices for element in anti_diag_lst)

                if is_anti_diag:
                    return True, anti_diag_lst
                           
        # find col-consecutive list  
        col_lst = list(range(index, index+(WINNING_CONDITION-1)*STATE_SHAPE[1]+1, STATE_SHAPE[1]))
        is_col = all(element in indices for element in col_lst)

        if is_col:
            return True, col_lst
                
    return False, []


def draw_omok_board(state, next_action=None, ax=None):
    state = copy.deepcopy(state)
    board = state[0] + state[1] * -1 if is_first_player(state) else state[0] * -1 + state[1]
    nrow, ncol = board.shape

    # create a figure for visualization
    if ax is None:
        _, ax = plt.subplots(figsize=(6,6))

    ax.set_xlim(0, ncol)
    ax.set_ylim(nrow,0)
    ax.set_facecolor('#d2a155')

    # draw the grid of Omok Board
    for i in range(-1, nrow + 1):
        ax.plot([i-0.5, i-0.5], [0.5, ncol-0.5], color='black', zorder=1)
        ax.plot([0.5, nrow-0.5], [i-0.5, i-0.5], color='black', zorder=1)

    # draw the pieces 
    for x in range(nrow):
        for y in range(ncol):
            if board[x, y] == 1:
                black_action = patches.Circle((y+0.5, x+0.5), 0.4, edgecolor='black', facecolor='black', zorder=3)
                ax.add_patch(black_action)

            elif board[x, y] == -1:
                white_action = patches.Circle((y+0.5, x+0.5), 0.4, edgecolor='black', facecolor='white', zorder=3)
                ax.add_patch(white_action)

    # if next action exists, draw it in the board 
    if next_action is not None:
        x, y = divmod(next_action, ncol)
        facecolor = 'black' if is_first_player(state) else 'white'

        next_action_patch = patches.Circle((y+0.5, x+0.5), 0.4, edgecolor='red', facecolor=facecolor, zorder=3)
        ax.add_patch(next_action_patch)

        state[0][x,y] = 1 

    # check consecutive and draw when it exists
    val, indices_lst = check_consecutive(state[0])

    if val is not True:
        val, indices_lst = check_consecutive(state[1])

    if val:
        result = list(map(divide, indices_lst))

        rows, cols = zip(*result)  
        rows, cols = list(rows) , list(cols) 

        ax.plot(cols, rows, color='#70d96b', marker='.', lw=2.5, zorder=4) 


    # Add title and labels 
    if next_action is None:
        ax.set_title(f"State : without next action")
    else:
        ax.set_title(f"State : with next action")

    # draw the red line above all elements
    ax.set_xticks(range(0, ncol))
    ax.set_yticks(range(0, nrow))
    ax.set_aspect('equal')


def visualize_MCTS_visits(visits, state, next_action=None, ax=None, agent_type='recent'):

    color_dict = {'best' : 'PuRd',
                  'recent' : 'GnBu'}
    
    visits = np.array(visits).reshape(STATE_SHAPE)

    board = state[0] + state[1] * -1 if is_first_player(state) else state[0] * -1 + state[1]
    nrow, ncol = board.shape

    if ax is None:
        _, ax = plt.subplots(figsize=(6,6))


    ax.set_xlim(0, ncol + 1)
    ax.set_ylim(nrow + 1, 0)
    ax.set_facecolor('#F5F5F5')

    # draw the grid of Omok Board
    for i in range(0, nrow + 1):
        ax.plot([i-0.5, i-0.5], [0.5, ncol-0.5], color='gray', alpha=0.5, zorder=1)
        ax.plot([0.5, nrow-0.5], [i-0.5, i-0.5], color='gray', alpha=0.5, zorder=1)

    # draw the pieces 
    for x in range(nrow):
        for y in range(ncol):
            if board[x, y] == 1:
                black_action = patches.Circle((y+0.5, x+0.5), 0.35, edgecolor='gray', facecolor='gray', zorder=2)
                ax.add_patch(black_action)

            elif board[x, y] == -1:
                white_action = patches.Circle((y+0.5, x+0.5), 0.35, edgecolor='gray', facecolor='white', zorder=2)
                ax.add_patch(white_action)

    if next_action is not None:
        x, y = divmod(next_action, ncol)
        facecolor = 'gray' if is_first_player(state) else 'white'

        new_action_patch = patches.Circle((y+0.5, x+0.5), 0.4, edgecolor='red', facecolor=facecolor, zorder=3)
        ax.add_patch(new_action_patch)

    
    annot_data = np.where(visits == 0, "", visits.astype(int))

    # Overlay the heatmap
    sns.heatmap(visits, ax=ax, square=True, annot=annot_data, cbar=True, fmt='', cmap=color_dict[agent_type], alpha=0.5, annot_kws={"size": 10, "weight": "bold"}, zorder=3)
    
    ax.set_title("MCTS visits")

def visualize_current_policy(policy, state, next_action=None, ax=None, agent_type='recent'):

    color_dict = {'best' : 'OrRd',
                  'recent' : 'BuPu'}
    
    policy = np.array(policy).reshape(STATE_SHAPE).round(2)

    board = state[0] + state[1] * -1 if is_first_player(state) else state[0] * -1 + state[1]
    nrow, ncol = board.shape

    if ax is None:
        _, ax = plt.subplots(figsize=(6,6))

    ax.set_xlim(0, ncol + 1)
    ax.set_ylim(nrow + 1, 0)
    ax.set_facecolor('#F5F5F5')

    # draw the grid of Omok Board
    for i in range(0, nrow + 1):
        ax.plot([i-0.5, i-0.5], [0.5, ncol-0.5], color='gray', alpha=0.5, zorder=1)
        ax.plot([0.5, nrow-0.5], [i-0.5, i-0.5], color='gray', alpha=0.5, zorder=1)

    # draw the pieces 
    for x in range(nrow):
        for y in range(ncol):
            if board[x, y] == 1:
                black_action = patches.Circle((y+0.5, x+0.5), 0.35, edgecolor='gray', facecolor='gray', zorder=2)
                ax.add_patch(black_action)

            elif board[x, y] == -1:
                white_action = patches.Circle((y+0.5, x+0.5), 0.35, edgecolor='gray', facecolor='white', zorder=2)
                ax.add_patch(white_action)

    if next_action is not None:
        x, y = divmod(next_action, ncol)
        facecolor = 'gray' if is_first_player(state) else 'white'

        new_action_patch = patches.Circle((y+0.5, x+0.5), 0.4, edgecolor='red', facecolor=facecolor, zorder=3)
        ax.add_patch(new_action_patch)

    
    annot_data = np.where(policy == 0, "", policy)

    # Overlay the heatmap
    sns.heatmap(policy, ax=ax, square=True, annot=annot_data, cbar=True, fmt='', cmap=color_dict[agent_type], alpha=0.5, annot_kws={"size": 10, "weight": "bold"}, zorder=3)
    # BuPu
    ax.set_title("current Policy")

def visualize_pack(agent_type, state, visit, policy, next_action, step=0, path=None, download=False):
    
    _, axes = plt.subplots(1, 3, figsize=(18, 6))

    draw_omok_board(state, next_action=next_action, ax=axes[0])
    visualize_MCTS_visits(visit, state, next_action=next_action, agent_type=agent_type, ax=axes[1])
    visualize_current_policy(policy, state, next_action=next_action, agent_type=agent_type, ax=axes[2])

    plt.tight_layout()
    plt.suptitle(agent_type, fontsize=26, fontweight='bold', y=1.02)

    if download:
        if path is None:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))
        plt.savefig(f"{path}/step_{step}.png", dpi=300, bbox_inches='tight')

    plt.show()

def visualize_game_result(result:dict, path=None, download=None):
    # 데이터 준비
    categories = list(result.keys())
    values = list(result.values())

    # 파이차트 그리기
    plt.figure(figsize=(6, 6))

    wedges, _, _ = plt.pie(
        values, 
        labels=categories,  # 카테고리 레이블
        autopct=lambda p: f'{p:.1f}%\n({int(p * sum(values) / 100)})',  # 비율과 개수 표시
        startangle=90,      # 시작 각도
        colors=['#76c893', '#f4d35e', '#e63946'],  # 색상 설정
        textprops=dict(color="black", fontsize=12, weight='bold')  # 텍스트 스타일
    )

    # 차트 제목
    plt.title("Game Results Distribution", fontsize=16, fontweight='bold')

    # 범례 추가
    plt.legend(wedges, categories, title="Results", loc="upper right", bbox_to_anchor=(1.2, 1))

    if download:
        if path is None:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))

        plt.savefig(f"{path}/loss.png", dpi=300, bbox_inches='tight')

    # 그래프 표시
    plt.show()

def visualize_game_record(game_action_list, ax=None, download=None, path=None):
    nrow, ncol = STATE_SHAPE

    # Create a figure for visualization
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
        ax.set_title("Game Record")

    ax.set_xlim(0, ncol)
    ax.set_ylim(nrow, 0)
    ax.set_aspect('equal')
    ax.set_facecolor('#d2a155')

    # Draw the grid of Omok Board
    for i in range(-1, nrow + 1):
        ax.plot([i - 0.5, i - 0.5], [0.5, ncol - 0.5], color='black', zorder=1)
        ax.plot([0.5, nrow - 0.5], [i - 0.5, i - 0.5], color='black', zorder=1)

    # Draw the pieces
    for idx, action in enumerate(game_action_list):
        x, y = divmod(action, ncol)

        if idx % 2 == 0:  # Black stone
            black_action = patches.Circle((y + 0.5, x + 0.5), 0.4, edgecolor='black', facecolor='black', zorder=2)
            ax.add_patch(black_action)
            ax.text(y + 0.5, x + 0.5, str(idx + 1), color='white', ha='center', va='center', fontsize=12, zorder=5)

        else:  # White stone
            white_action = patches.Circle((y + 0.5, x + 0.5), 0.4, edgecolor='black', facecolor='white', zorder=2)
            ax.add_patch(white_action)
            ax.text(y + 0.5, x + 0.5, str(idx + 1), color='black', ha='center', va='center', fontsize=12, zorder=5)
    

    # check consecutive and draw when it exists
    black_indices = game_action_list[::2]
    white_indices = game_action_list[1::2]

    val, indices_lst = check_consecutive(black_indices)

    if val is not True:
        val, indices_lst = check_consecutive(white_indices)

    if val:
        result = list(map(divide, indices_lst))

        rows, cols = zip(*result)  
        rows, cols = list(rows) , list(cols) 

        ax.plot(cols, rows, color='#70d96b', marker='.', lw=2.5, alpha=1.0, zorder=4) 

    if download:
        if path is None:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))

        plt.savefig(f"{path}/game_record.png", dpi=300, bbox_inches='tight')

def visualize_win_rate(win_rates, ax=None, path=None, download=False):
    # Create a figure for visualization
    show_plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        show_plot = True  # 새 figure를 생성한 경우 show 활성화

    # Separate data
    win, win_draw = zip(*win_rates)

    # Graphing
    ax.plot(win, linestyle='-', label="win_draw")
    ax.plot(win_draw, linestyle='-', label="win")

    # X-axis settings
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))  # x축에 10개의 값만 표시

    ax.set_xlabel("steps")
    ax.set_ylabel("rate")
    ax.set_title("Win and Win Draw Rate per Steps")
    ax.legend()
    
    # Remove grid
    ax.grid(False)

    if download:
        if path is None:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))
        plt.savefig(f"{path}/win_rate.png", dpi=300, bbox_inches='tight')

    if show_plot:
        plt.show()

def visualize_loss(losses, ax=None, path=None, download=False):
    # Create a figure for visualization
    show_plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        show_plot = True  # 새 figure를 생성한 경우 show 활성화

    # Separate data
    p, v, total = zip(*losses)

    # Graphing
    ax.plot(p, linestyle='-', label="policy")
    ax.plot(v, linestyle='-', label="value")
    ax.plot(total, linestyle='-', label="total")

    # X-axis settings
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))  # x축에 10개의 값만 표시

    ax.set_xlabel("steps")
    ax.set_ylabel("loss")
    ax.set_title("Loss per Steps")
    ax.legend()
    
    # Remove grid
    ax.grid(False)

    if download:
        if path is None:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))
        plt.savefig(f"{path}/loss.png", dpi=300, bbox_inches='tight')

    if show_plot:
        plt.show()