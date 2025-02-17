const canvas = document.getElementById("boardCanvas");
const ctx = canvas.getContext("2d");

// 내부 해상도를 2배 증가 (720x720)
const displaySize = 360;
const highResSize = 720;
canvas.width = highResSize;
canvas.height = highResSize;
canvas.style.width = `${displaySize}px`;
canvas.style.height = `${displaySize}px`;

ctx.scale(2, 2);  // 모든 그리기 작업을 2배로 확대
ctx.imageSmoothingEnabled = true;  // 안티앨리어싱 활성화

const gridSize = 9;
const cellSize = displaySize / gridSize;
const stoneRadius = cellSize * 0.4;
let isWhite = 1; // 1 = 백돌, 0 = 흑돌
let startFlag = 0; // 0 = 시작 안함, 1 = 시작 함 
let isDone = 0;
let isPlayerTurn = 0; 

// 1️⃣ 선공(initiative) 결정 
function pickInitiative() {
    if (startFlag === 1) {
        alert("게임이 이미 시작되었습니다! 선공을 변경할 수 없습니다.");
        return;
    }
    isWhite = (isWhite === 1) ? 0 : 1; // 0과 1을 번갈아가며 변경

    isPlayerTurn = (isWhite === 0) ? 1 : 0; // 만약 플레이어가 흑돌을 선택했으면 선이다. 

    // 이미지 변경 (백돌 또는 흑돌)
    const isInit = document.getElementById("is_init");
    isInit.src = isWhite === 1 ?
        "/static/white.png" : "/static/black.png"; 

    alert(`선공: ${isWhite === 1 ? "백돌" : "흑돌"}`);
}

function updateResultBoard(data) {
    console.log("updateResultBoard 호출됨:", data); // 🛠 디버깅 추가

    const gameResult = data.game_result;
    const isPlayerTurn = data.is_player_turn; // 서버 응답에서 값을 가져오기

    const gameResultImg = document.getElementById("gameResultImg");

    console.log("게임 결과 값:", gameResult);
    console.log("현재 플레이어 턴:", isPlayerTurn);

    // 결과가 2(게임 진행 중)이면 변경하지 않음
    if (gameResult === 2) {
        gameResultImg.src = "/static/default.png";
    }

    // 플레이어가 승리한 경우
    if (gameResult === 0 && isPlayerTurn === 1) {
        gameResultImg.src = "/static/win.png";
        isDone = 1;
    } 
    // AI가 승리한 경우
    else if (gameResult === 0 && isPlayerTurn === 0) {
        gameResultImg.src = "/static/lose.png";
        isDone = 1;
    }    
    // 무승부
    else if (gameResult === 1) {
        gameResultImg.src = "/static/draw.png";
        isDone = 1;
    }
    else {
        gameResultImg.src = "/static/default.png";
    }
}

function start() {
    if (startFlag === 1) {
        alert("게임이 이미 시작되었습니다! 다시 시작하려면 Reset 버튼을 눌러주세요.");
        return;
    }
    startFlag = (startFlag === 0) ? 1 : 0; 
    alert("게임이 시작되었습니다!")
}

async function resetBoard() {
    try {
        const response = await axios.post('/reset-board');
        fetchBoard(); // 바둑판 리셋 후 업데이트
        startFlag = 0;
        isDone = 0;
        alert("게임이 초기화되었습니다.");
    } catch (error) {
        console.error("바둑판 초기화 오류:", error);
    }
}

async function fetchBoard() {
    try {
        const response = await axios.get('http://127.0.0.1:5000/get-board');
        console.log("서버 응답 데이터:", response.data);  // 🛠 디버깅 추가
        renderBoard(response.data.board);
        updateResultBoard(response.data);
    } catch (error) {
        console.error("바둑판 상태 가져오기 오류:", error);
    }
}

let isUpdating = false; // 요청 중인지 여부를 저장하는 플래그

async function placeStone(x, y) {
    if (startFlag === 0) {
        alert("게임 시작 전에는 수를 둘 수 없습니다. Start 버튼을 눌러주세요.");
        return;
    }

    if (isUpdating) {
        alert("이전 수가 반영되는 중입니다. 잠시만 기다려주세요!");
        return;
    }

    if (isDone) {
        alert("게임이 종료되었습니다. 새로운 수를 둘 수 없습니다.");
        return;
    }

    isUpdating = true; // 요청 시작 시 업데이트 플래그 활성화
    document.getElementById("boardCanvas").style.pointerEvents = "none"; // 사용자 입력 차단

    try {
        const response = await axios.post('http://127.0.0.1:5000/update-board', { x, y, isWhite: isWhite });
        if (response && response.data) {
            console.log("update-board 응답:", response.data);  // 🛠 디버깅 추가
            await fetchBoard();  // 성공하면 보드 업데이트
        } else {
            console.error("서버 응답이 없습니다.", response);
        }
    } catch (error) {
        console.error("돌 놓기 오류:", error);
        if (error.response && error.response.data && error.response.data.message) {
            alert(error.response.data.message); // 중복 놓기 방지
        } else {
            alert("알 수 없는 오류가 발생했습니다.");
        }
    } finally {
        isUpdating = false; // 요청 완료 후 플래그 해제
        document.getElementById("boardCanvas").style.pointerEvents = "auto"; // 사용자 입력 허용
    }
}

function drawBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 격자선 두껍게 조정
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";

    for (let i = 0; i < gridSize; i++) {
        let pos = (i + 0.5) * cellSize; // 중앙 맞추기
        ctx.beginPath();
        ctx.moveTo(pos, cellSize * 0.5);
        ctx.lineTo(pos, displaySize - cellSize * 0.5);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(cellSize * 0.5, pos);
        ctx.lineTo(displaySize - cellSize * 0.5, pos);
        ctx.stroke();
    }
}

function renderBoard(board) {
    drawBoard();

    for (let x = 0; x < gridSize; x++) {
        for (let y = 0; y < gridSize; y++) {
            if (board[0][y][x] === 1 || board[1][y][x] === 1) {
                drawStone(y, x, board[0][y][x] === 0 ? "white" : "black");
            }
        }
    }
}

function drawStone(x, y, color) {
    const centerX = (x + 0.5) * cellSize;
    const centerY = (y + 0.5) * cellSize;

    ctx.beginPath();
    ctx.arc(centerX, centerY, stoneRadius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();
}

canvas.addEventListener("click", function (event) {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / cellSize);
    const y = Math.floor((event.clientY - rect.top) / cellSize);
    placeStone(x, y);
});


document.getElementById("startButt").addEventListener("click", async function () {
    try {
        console.log("Start 버튼 클릭: isPlayerTurn =", isPlayerTurn); // 디버깅 로그 추가

        const response = await fetch('/trigger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // JSON 타입 명시
            },
            body: JSON.stringify({ isPlayerTurn: isPlayerTurn })  // JSON 데이터 변환
        });

        const data = await response.json();
        console.log("trigger_action 응답:", data);

        fetchBoard();  // AI가 둔 후 즉시 보드 갱신

    } catch (error) {
        console.error("AI 수를 두는 중 오류 발생:", error);
    }
});

// function fetchBoardPeriodically() {
//     setInterval(async () => {
//         const response = await axios.get('/get-board');
//         renderBoard(response.data);
//     }, 1000); // 1초마다 서버에서 바둑판 상태를 가져옴
// }

fetchBoard(); // 페이지 로드 시 보드 불러오기
// fetchBoardPeriodically();