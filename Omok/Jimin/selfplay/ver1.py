from state.ver1 import *
from MCTS.ver1 import *

class SelfPlay:
    def __init__(self, model, temp, temp_discount, sp_game_count, pv_evaluate_count):
        # model
        self.model = model

        # params
        self.sp_game_count = sp_game_count
        self.pv_evaluate_count = pv_evaluate_count

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

            learned_policy[state.legal_actions] = legal_policy

            history.append([state.board, learned_policy, None]) # board, policy, value (원래는 떨어트리는게 맞지만, 틱택토는 간단한 환경임으로 시간 순으로 누적하지 않는다.)

            # 정책에 따른 행동 구하기
            action = np.random.choice(state.legal_actions, p=legal_policy)

            # step
            state = state.next(action)

        # ====== history : value 일괄 업데이트 ======
        # end state 가치 기준
        value = self.get_first_player_value(state)

        for i in range(len(history)):
            history[i][-1] = value
            value = -value

        # discount temp
        self.temp = 1 if i < 30 else self.temp * self.temp_discount

        return history

    def _self_play(self):
        # sp_game_count 횟수 만큼 single play 시행
        for i in range(self.sp_game_count):
            single_history = self._single_play(i)
            self.history.extend(single_history)

            if (i+1) % (self.sp_game_count // 10) == 0:
                print(f"self play {i+1} / {self.sp_game_count}")

    def __call__(self):
        self.mcts = MCTS(self.pv_evaluate_count)
        self._self_play()

    def update_model(self, model):
        self.model.load_state_dict(model.state_dict())