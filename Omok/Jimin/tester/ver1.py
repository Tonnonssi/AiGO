import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from MCTS.ver1 import *
from main.hyperParams import *
from state.ver2 import *
# from state.ver1 import *

class ModelvsHuman:
    def __init__(self, model):
        self.model = model
        self.mcts = MCTS(EVAL_GAME_COUNT)
        self.get_next_actions = self.mcts.get_legal_actions_of(model, 0)

    def render(self, state):

        board = state.board[0] + (-1 * state.board[1]) if state.is_first_player() else state.board[1] + (-1 * state.board[0])

        def pattern(x):
            if x == 1:
                return 'O'
            elif x == 0:
                return ' '
            else:
                return 'X'

        df = pd.DataFrame(board)
        df = df.map(pattern)
        display(df)

    def vs_human(self, with_policy):
        state = State()
        self.render(state)

        while True:
            if state.is_done():
                break

            else:
                action = self.get_next_actions(state)
                learned_policy = np.zeros(state.n_actions)

                legal_policy = self.mcts.legal_policy
                learned_policy[state.legal_actions] = legal_policy

                if  with_policy:
                    hist = (state.board, learned_policy, None)
                    visualize_history(hist)

                state = state.next(action)


                print(f"Alpha Zero's Action is : {action}")
                self.render(state)


                my_action = int(input("Choose Your Action : "))
                state = state.next(my_action)
                self.render(state)

    def __call__(self, with_policy=True):
        self.vs_human(with_policy)


def visualize_history(history):

    state, learned_policy, _ = history
    learned_policy = np.array(learned_policy).reshape(STATE_SHAPE)

    def make_coord(state):
        mask = state.astype(bool).reshape(-1)  # 불리언 마스크 생성
        indices = list(np.arange(len(mask))[mask])  # True인 인덱스 추출

        # 배열의 열 크기 (state는 2D 배열로 가정)
        width = state.shape[1]

        # divmod로 몫과 나머지를 계산
        if len(indices) != 0:
            quotients, remainders = zip(*[divmod(index, width) for index in indices])
            coords = [quotients, remainders]

        else:
            coords = None

        return coords

    # Plotting
    _, ax = plt.subplots()
    cax = ax.matshow(learned_policy, cmap='Greens', alpha=0.7)

    # Turn 인식
    if state[-1].all() == 0:  # 0이 첫 턴인 경우
        o_coords = make_coord(state[0])
        x_coords = make_coord(state[1])
        if o_coords is not None:
            plt.scatter(o_coords[1], o_coords[0], marker="o", s=2000, c='black')  # x, y 좌표로 매핑
            plt.scatter(o_coords[1], o_coords[0], marker="o", s=1500, c='#F2F2F2')
        if x_coords is not None:
            plt.scatter(x_coords[1], x_coords[0], marker="x", s=2000, c='black', linewidths=3.0)
    else:
        o_coords = make_coord(state[1])
        x_coords = make_coord(state[0])
        if o_coords is not None:
            plt.scatter(o_coords[1], o_coords[0], marker="o", s=2000, c='black')  # x, y 좌표로 매핑
            plt.scatter(o_coords[1], o_coords[0], marker="o", s=1500, c='#F2F2F2')

        if x_coords is not None:
            plt.scatter(x_coords[1], x_coords[0], marker="x", s=2000, c='black', linewidths=3.0)

    max_coord = divmod(np.argmax(learned_policy), len(state[1]))

    if state[-1].all() == 0:
        plt.scatter(max_coord[1], max_coord[0], marker="o", s=2000, c='red', linewidths=3.0) # #FF19A3
    else:
        plt.scatter(max_coord[1], max_coord[0], marker="x", s=2000, c='red', linewidths=3.0) # #FF19A3


    # Add text annotations (optional)
    for (i, j), value in np.ndenumerate(learned_policy):
        if value != 0.0:
            ax.text(j, i, f"{value:.2f}", ha='center', va='center', fontsize='15',
                    fontweight='bold' if value == np.max(learned_policy) else "normal",
                    color="white" if value == np.max(learned_policy) else "black")

    # Colorbar and titles
    plt.colorbar(cax, ax=ax)
    ax.set_title("Current State, Policy with Highlighted Highest Action")
    ax.axis("off")
    plt.show()