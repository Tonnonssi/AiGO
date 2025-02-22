import sys
import os

# 현재 파일(server.py)이 있는 경로 기준으로 상위 디렉토리(AiGO)를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template
import numpy as np

from Omok.state import *
from Omok.MCTS import *
from models.load_model import *

# web utils 
app = Flask(__name__)

# State / board 
State = select_state(STATE_DIM)
state = State()
board = np.zeros((2, 9, 9), dtype=int)

# game status 
game_result = 2 # (win, draw, continue)
is_player_turn = None
is_second_player = None

# alpha zero setting
mcts = MCTS(N_PLAYOUT)
get_next_action = mcts.get_legal_actions_of(model, 0, with_policy=False)

@app.route('/')
def home():
    """ 기본 페이지 제공 """
    return render_template('index.html')


@app.route('/get-board', methods=['GET'])
def get_board():
    global board, game_result, is_player_turn
    print(game_result, is_player_turn)
    """ 현재 바둑판 상태 반환 """
    return jsonify({"board": board.tolist(),
                    "game_result" : game_result,
                    "is_player_turn" : int(not(is_player_turn))
                    })


@app.route('/update-board', methods=['POST'])
def update_board():
    """ 프런트에서 돌을 놓으면 업데이트 """
    global board, state, is_second_player, is_player_turn
    data = request.json
    print(data)
    x, y, is_second_player = data["x"], data["y"], data["isWhite"] # player | 1 = white : 0 = black

    if board[0, x, y] == 1 or board[1, x, y] == 1:
        return jsonify({"message": "이미 돌이 있는 자리입니다."}), 400
    
    value = place_stone_by_human(x, y, is_second_player)  
  
    if not state.is_done():
        # time.sleep(5)
        value = place_stone_by_AI(is_second_player)

    else:
        return value 
    
    return value 
    


def place_stone_by_human(x, y, player):
    global board, state, is_player_turn, game_result
    
    board[player, x, y] = 1  # 해당 위치에 돌 놓기

    action_idx = x*9 + y
    state = state.next(action_idx)
    print(state)

    game_result = get_game_result(state) # ( 0 : win, 1 : draw, 2 : continue )
    is_player_turn = 0 # 순서 업데이트 

    return jsonify({"message": "돌이 놓였습니다.", 
                    "board": board.tolist(),
                    "game_result" : game_result,
                    "is_AI" : 0 })


def place_stone_by_AI(is_second_player):
    global board, state, is_player_turn, game_result

    ai_board_idx = int(not is_second_player)
    action = get_next_action(state)  # AI의 다음 수 결정
    x, y = divmod(action, 9)

    board[ai_board_idx, x, y] = 1  # AI가 돌을 놓음
    state = state.next(action)  
    print(state)

    game_result = get_game_result(state)
    is_player_turn = 1 # 순서 업데이트 

    return jsonify({
        "message": "AI가 돌을 놓았습니다.", 
        "board": board.tolist(),
        "game_result": game_result,
        "is_AI": 1 })


def get_game_result(state):
    if not state.is_done():
        return 2 # continue
    
    if state.is_lose():
        return 0 # win (플레이어 관계가 뒤바뀐 상태이기 때문에 lose -> win)
    
    else:
        return 1 # draw

@app.route('/reset-board', methods=['POST'])
def reset_board():
    """ 바둑판 초기화 """
    global board, state
    board = np.zeros((2, 9, 9), dtype=int)  # 모든 값 0으로 초기화
    state = State() # state 초기화 
    return jsonify({"message": "바둑판이 초기화되었습니다.", "board": board.tolist()})

@app.route('/trigger', methods=['POST'])
def trigger_action():
    global is_second_player, is_player_turn

    """버튼이 눌렸을 때 실행되는 서버 함수"""
    try:
        data = request.get_json(force=True)  # force=True 추가하여 JSON 강제 파싱
        print("trigger_action 요청 데이터:", data)  # 디버깅 로그 추가

        if not data:
            return jsonify({"error": "요청에 JSON 데이터가 없습니다."}), 400
        
        is_player_turn = data.get("isPlayerTurn")  # 기본값 None
        is_second_player = 1

        if is_player_turn is None:
            return jsonify({"error": "isPlayerTurn 값이 전달되지 않았습니다."}), 400

        if not is_player_turn:
            return place_stone_by_AI(is_second_player)  # AI가 수를 둠

        return jsonify({"message": "플레이어의 차례입니다."})

    except Exception as e:
        print(f"trigger_action() 에러 발생: {e}")  # 터미널에 오류 출력
        return jsonify({"error": "서버 내부 오류 발생", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)