import cv2
import numpy as np

def analyze_omok_board(image_path, cell_size=30, grid_size=19,
                       show_grid=True, improve_detection=True):
    """
    analyze_omok_board(image_path : str,
                       cell_size : int,
                       grid_size : int,
                       show_grid : bool,
                       improve_detection : bool)
    -> return (state : numpy.ndarray, black_stones : list, white_stones : list)
    ---------------------------------------------------------------------------
    바둑판 이미지를 분석하여 상태 배열, 검은돌 좌표, 흰돌 좌표를 반환합니다.
    show_grid=True일 경우, 격자점과 검출된 돌을 이미지에 표시하여 띄웁니다.
    improve_detection=True일 경우, 모폴로지 연산 등 추가 전처리를 적용합니다.
    """

    # 1) 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

    # 2) 작업용 복사본
    image_copy = image.copy()

    # 3) 흑백 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # --- (옵션) 검출 정확도 향상을 위한 전처리 ---
    if improve_detection:
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # 4) 엣지 검출
    edges = cv2.Canny(gray, 100, 200)

    # (옵션) 모폴로지 연산(팽창->침식)으로 엣지 보완
    if improve_detection:
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.erode(edges, kernel, iterations=1)

    # 5) 허프 변환을 이용한 직선 검출 (직접 사용하지 않아도 남겨둠)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=40,
        maxLineGap=5
    )

    # 6) 바둑판 중심 계산(이미지 중심 가정)
    center_x = image.shape[1] // 2  # 가로 중심 (width)
    center_y = image.shape[0] // 2  # 세로 중심 (height)

    # 7) 격자 중심 좌표(교차점) 계산 함수
    def calculate_grid_centers(cx, cy, g_size, c_size):
        half_grid = g_size // 2
        centers = []
        for row in range(-half_grid, half_grid + 1):
            for col in range(-half_grid, half_grid + 1):

                grid_center_x = cx + col * c_size
                grid_center_y = cy + row * c_size
                centers.append((grid_center_x, grid_center_y))
        return centers

    # 격자 중심 좌표 구하기
    grid_centers = calculate_grid_centers(center_x, center_y, grid_size, cell_size)

    # 시각화(옵션)
    if show_grid:
        for (gx, gy) in grid_centers:
            # 초록색 작은 원으로 격자점 표시
            cv2.circle(image_copy, (gx, gy), 2, (0, 255, 0), -1)

    # 8) 바둑판 상태 배열 초기화
    state = np.zeros((grid_size, grid_size), dtype=int)

    # 9) 원 검출(바둑돌 검출)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=100,   # Canny 에지 상한값 (너무 낮으면 잡음까지 에지로 인식)
        param2=18,    # 원 검출 결과의 임계값 (높을수록 엄격)
        minRadius=5,
        maxRadius=13
    )

    # 10) 바둑돌과 격자 매칭
    if circles is not None:
    # circles는 shape (1, N, 3) 형태를 가짐
    # .around()는 반올림, .astype(np.int32)는 정수형(32비트 부호 있음)으로 변환
        circles = np.around(circles[0]).astype(np.int32)
        for circle in circles:
            x, y, r = circle  # 이제 x, y, r은 int(부호 있는 정수)
            
            # 이하 동일
            cv2.circle(image_copy, (x, y), r, (255, 0, 0), 2)
            
            for idx, (grid_x, grid_y) in enumerate(grid_centers):
                row, col = divmod(idx, grid_size)
                # 여기서 x, y, grid_x, grid_y가 부호있는 int 이므로 음수 가능
                if abs(grid_x - x) <= cell_size // 2 and abs(grid_y - y) <= cell_size // 2:
                    roi = gray[max(y - r, 0): y + r, max(x - r, 0): x + r]
                    mean_intensity = np.mean(roi)

                    if mean_intensity < 150:   # 흑돌
                        state[row, col] = 1
                    elif mean_intensity > 160: # 백돌
                        state[row, col] = -1


    # 11) 돌 좌표 리스트 추출
    black_stones = np.argwhere(state == 1).tolist()
    white_stones = np.argwhere(state == -1).tolist()

    # (로컬) 시각화 결과 보기
    if show_grid:
        cv2.imshow("Analyzed Omok Board", image_copy)
        cv2.waitKey(0)  # 아무 키나 누를 때까지 대기
        cv2.destroyAllWindows()

    start = 0  # 5
    end = 9  # 14

    center_state = state[start:end, start:end]

    center_black_stones = [
            (r - start, c - start)
            for (r, c) in black_stones
            if start <= r < end and start <= c < end
        ]
    center_white_stones = [
            (r - start, c - start)
            for (r, c) in white_stones
            if start <= r < end and start <= c < end
        ]
    # 12) 결과 반환
    return center_state, center_black_stones, center_white_stones


if __name__ == "__main__":
    # 로컬 경로 예시
    image_path = "omokk3.jpg"

    state, black_stones, white_stones = analyze_omok_board(
        
        image_path=image_path,
        cell_size=26,
        grid_size=9,
        show_grid=True,        # 격자 및 검출된 돌 시각화
        improve_detection=True # 모폴로지 연산 등으로 돌 검출 정확도 향상
    )

    print("State Array:\n", state)
    print("Black Stones:", black_stones)
    print("White Stones:", white_stones)
