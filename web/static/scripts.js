const canvas = document.getElementById("boardCanvas");
const ctx = canvas.getContext("2d");

// 내부 해상도를 2배 증가 (720x720)
const displaySize = 360;
const highResSize = 720;
canvas.width = highResSize;
canvas.height = highResSize;
canvas.style.width = `${displaySize}px`;
canvas.style.height = `${displaySize}px`;

ctx.scale(2, 2);
ctx.imageSmoothingEnabled = true;

const gridSize = 9;
const cellSize = displaySize / gridSize;
const stoneRadius = cellSize * 0.4;
let isWhite = 1;
let startFlag = 0;
let isDone = 0;
let isPlayerTurn = 0;
let isUpdating = false;

function pickInitiative() {
    if (startFlag) {
        alert("게임이 이미 시작되었습니다! 선공을 변경할 수 없습니다.");
        return;
    }
    if (isDone) {
        isDone = 0; // 게임이 끝난 후 선공을 바꿀 때 isDone 초기화
    }
    isWhite = 1 - isWhite;
    isPlayerTurn = isWhite ? 0 : 1;
    document.getElementById("is_init").src = isWhite ? "/static/white.png" : "/static/black.png";
    alert(`선공: ${isWhite ? "백돌" : "흑돌"}`);
}

function updateResultBoard(data) {
    console.log("updateResultBoard 호출됨:", data);
    const gameResultImg = document.getElementById("gameResultImg");

    if (data.game_result === 2) {
        gameResultImg.src = "/static/default.png";
        return;
    }

    if (!startFlag) {
        return; // 게임이 시작되지 않았으면 isDone을 갱신하지 않음
    }

    isDone = 1;
    gameResultImg.src = data.game_result === 1 ? "/static/draw.png" :
                        data.is_player_turn ? "/static/win.png" : "/static/lose.png";
}

function start() {
    if (startFlag) {
        alert("게임이 이미 시작되었습니다! 다시 시작하려면 Reset 버튼을 눌러주세요.");
        return;
    }
    startFlag = 1;
    isDone = 0;
    alert("게임이 시작되었습니다!");
}

async function resetBoard() {
    try {
        await axios.post('/reset-board');
        fetchBoard();
        startFlag = 0;
        isDone = 0;
        alert("게임이 초기화되었습니다.");
    } catch (error) {
        console.error("바둑판 초기화 오류:", error);
    }
}

async function fetchBoard() {
    try {
        const response = await axios.get('/get-board');
        console.log("서버 응답 데이터:", response.data);
        renderBoard(response.data.board);
        updateResultBoard(response.data);
        
        // 🛠 보드 업데이트 후 isDone 초기화
        if (startFlag === 1) {
            isDone = 0;
        }

    } catch (error) {
        console.error("바둑판 상태 가져오기 오류:", error);
    }
}

async function placeStone(x, y) {
    if (!startFlag) {
        alert("게임 시작 전에는 수를 둘 수 없습니다. Start 버튼을 눌러주세요.");
        return;
    }
    if (isUpdating || isDone) {
        alert(isDone ? "게임이 종료되었습니다." : "이전 수가 반영되는 중입니다.");
        return;
    }

    isUpdating = true;
    document.getElementById("boardCanvas").style.pointerEvents = "none";

    try {
        const response = await axios.post('/update-board', { x, y, isWhite });
        if (response?.data) {
            console.log("update-board 응답:", response.data);
            await fetchBoard();
        }
    } catch (error) {
        console.error("돌 놓기 오류:", error);
        alert(error.response?.data?.message || "알 수 없는 오류가 발생했습니다.");
    } finally {
        isUpdating = false;
        document.getElementById("boardCanvas").style.pointerEvents = "auto";
    }
}

function drawBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";

    for (let i = 0; i < gridSize; i++) {
        let pos = (i + 0.5) * cellSize;
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
            if (board[0][y][x] || board[1][y][x]) {
                drawStone(y, x, board[0][y][x] ? "black" : "white");
            }
        }
    }
}

function drawStone(x, y, color) {
    ctx.beginPath();
    ctx.arc((x + 0.5) * cellSize, (y + 0.5) * cellSize, stoneRadius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();
}

canvas.addEventListener("click", (event) => {
    const rect = canvas.getBoundingClientRect();
    placeStone(
        Math.floor((event.clientX - rect.left) / cellSize),
        Math.floor((event.clientY - rect.top) / cellSize)
    );
});

document.getElementById("startButt").addEventListener("click", async () => {
    try {
        console.log("Start 버튼 클릭: isPlayerTurn =", isPlayerTurn);
        await fetch('/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ isPlayerTurn })
        });
        isDone = 0;
        fetchBoard();
    } catch (error) {
        console.error("AI 수를 두는 중 오류 발생:", error);
    }
});

fetchBoard();