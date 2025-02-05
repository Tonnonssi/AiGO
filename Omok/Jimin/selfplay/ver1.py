from state.ver2 import *
# from state.ver1 import *
# from MCTS.ver2 import *
from MCTS.ver1 import *

class SelfPlay:
    def __init__(self, model, temp, temp_discount, n_selfplay, n_playout):
        # model
        self.model = model

        # params
        self.n_selfplay = n_selfplay
        self.n_playout = n_playout

        # about temps
        self.temp = temp
        self.temp_discount = temp_discount

        self.history = [] # selfPlay's yield

        # mcts는 call할 때마다 새로운 객체가 불러와져야 한다. 
        self.mcts = None 

        
    def get_first_player_value(self, ended_state):
        # 1: 선 수 플레이어 승리, -1: 선 수 플레이어 패배, 0: 무승부
        if ended_state.is_lose():
            return -1 if ended_state.is_first_player() else 1
        return 0

    def _single_play(self, i):

        history = []
        state = State()

        while True:
            if state.is_done():
                break

            # 현 상태에 대한 정책 구하기
            learned_policy = np.zeros([state.n_actions]) # init value

            legal_policy = self.mcts.get_legal_policy(state, self.model, self.temp) # MCTS로 정책 생성 # *****

            learned_policy[state.get_legal_actions()] = legal_policy
            
            # ===== 수정한 부분 ======
            # 원래는 논문대로 플레이어 순서를 state에 포함해 구현했다. 
            # 하지만 성능이 제대로 나오지 않았고, 원래 레퍼런스 대로 state를 바꾼다. 
            history.append([state(), learned_policy, None]) # board, policy, value (원래는 떨어트리는게 맞지만, 틱택토는 간단한 환경임으로 시간 순으로 누적하지 않는다.)

            # 정책에 따른 행동 구하기
            action = np.random.choice(state.get_legal_actions(), p=legal_policy)

            # step
            state = state.next(action)

        # ====== history : value 일괄 업데이트 ======
        # end state 가치 기준
        value = self.get_first_player_value(state)

        for i in range(len(history)):
            history[i][-1] = value
            value = -value

        return history

    def _self_play(self):
        # n_selfplay 횟수 만큼 single play 시행
        for i in range(self.n_selfplay):
            single_history = self._single_play(i)
            self.history.extend(single_history)

            if (i+1) % (self.n_selfplay // 10) == 0:
                print(f"self play {i+1} / {self.n_selfplay}")

    def __call__(self, idx):
        self.mcts = MCTS(self.n_playout)
        self._self_play()
         # discount temp
        self.temp = 1 if idx < 30 else self.temp * self.temp_discount

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())