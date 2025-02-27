import cv2
import numpy as np
from sklearn.cluster import KMeans

def analyze_omok_board_19x19(
    image_path="omok.jpg",
    show_result=True
):
    """
    analyze_omok_board_19x19(image_path : str, show_result : bool) 
    -> return (state : numpy.ndarray, black_stones : list, white_stones : list)
    ---------------------------------------------------------------------------
    1) 허프 변환(HoughLinesP)으로 19개의 가로/세로 줄을 찾아 바둑판 교차점 검출
    2) KMeans(n_clusters=361)로 교차점을 361개로 묶어 (19x19) 격자 형태로 정렬
    3) 각 교차점 주변(예: 20×20 영역)의 밝기로 돌(흑, 백) 또는 빈칸을 판정
    4) 흑돌과 백돌 좌표, 전체 상태 배열을 반환
    """
    # 1) 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2) 엣지 검출
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 3) 허프 변환으로 선 검출
    lines = cv2.HoughLinesP(
        edges, 
        1, 
        np.pi / 180, 
        100, 
        minLineLength=50, 
        maxLineGap=20
    )
    if lines is None or len(lines) == 0:
        raise ValueError("유효한 선을 검출하지 못했습니다.")

    # 4) 가로/세로 선 분류
    horizontal_lines = []
    vertical_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if abs(y2 - y1) < 10:  # 거의 수평
                horizontal_lines.append((x1, y1, x2, y2))
            elif abs(x2 - x1) < 10:  # 거의 수직
                vertical_lines.append((x1, y1, x2, y2))

    # 5) 선 병합(가까운 선은 하나로 처리)
    def merge_lines(lines, orientation, threshold=20):
        if orientation == "horizontal":
            key_func = lambda x: x[1]  # y1로 정렬
        else:  # vertical
            key_func = lambda x: x[0]  # x1로 정렬

        lines = sorted(lines, key=key_func)
        merged = []
        for line in lines:
            if not merged:
                merged.append(line)
                continue
            prev_line = merged[-1]
            if orientation == "horizontal":
                if abs(line[1] - prev_line[1]) > threshold:
                    merged.append(line)
            else:  # vertical
                if abs(line[0] - prev_line[0]) > threshold:
                    merged.append(line)
        return merged

    horizontal_lines = merge_lines(horizontal_lines, "horizontal")
    vertical_lines = merge_lines(vertical_lines, "vertical")

    # 6) 19개 라인 보정
    def ensure_n_lines(lines, orientation, n=19):
        if orientation == "horizontal":
            lines = sorted(lines, key=lambda x: x[1])  # y1 기준
            positions = [line[1] for line in lines]   # y1
        else:
            lines = sorted(lines, key=lambda x: x[0])  # x1 기준
            positions = [line[0] for line in lines]    # x1

        # 라인이 n개보다 적으면 중간값 보간해서 추가
        if len(positions) < n:
            for _ in range(n - len(positions)):
                for i in range(len(positions) - 1):
                    mid = (positions[i] + positions[i + 1]) // 2
                    if mid not in positions:
                        positions.append(mid)
                        break
            positions = sorted(positions)

        # positions를 기반으로 라인 생성
        if orientation == "horizontal":
            return [(0, pos, img.shape[1], pos) for pos in positions]
        else:
            return [(pos, 0, pos, img.shape[0]) for pos in positions]

    horizontal_lines = ensure_n_lines(horizontal_lines, "horizontal", n=19)
    vertical_lines = ensure_n_lines(vertical_lines, "vertical", n=19)

    # 7) 교차점 계산
    intersections = []
    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            x1, y1, x2, y2 = h_line
            x3, y3, x4, y4 = v_line
            det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if det != 0:  # 평행하지 않으면 교차점 존재
                px = ((x1 * y2 - y1 * x2) * (x3 - x4) - 
                      (x1 - x2) * (x3 * y4 - y3 * x4)) / det
                py = ((x1 * y2 - y1 * x2) * (y3 - y4) - 
                      (y1 - y2) * (x3 * y4 - y3 * x4)) / det
                intersections.append((int(px), int(py)))

    if len(intersections) == 0:
        raise ValueError("격자 교차점을 찾지 못했습니다.")

    # 8) 19x19 = 361점으로 KMeans 클러스터링
    intersections_np = np.array(intersections)
    kmeans = KMeans(n_clusters=361, random_state=42)
    kmeans.fit(intersections_np)
    cluster_centers = kmeans.cluster_centers_  # 361개 중심점

    # 9) state 배열(19x19) 생성
    state = np.zeros((19, 19), dtype=int)

    # 10) 교차점 정렬 (y좌표->x좌표 순)
    sorted_centers = sorted(cluster_centers, key=lambda x: (x[1], x[0]))
    # 19줄로 나누기
    grid_centers = [sorted_centers[i * 19:(i + 1) * 19] for i in range(19)]

    # 11) 돌 좌표 판별: 흑(1), 백(-1), 빈칸(0)
    for row_idx, row in enumerate(grid_centers):
        for col_idx, (px, py) in enumerate(row):
            px, py = int(px), int(py)
            # 교차점 주변을 작은 사각형으로 잘라 평균 밝기 계산
            rmin = max(py - 10, 0)
            rmax = min(py + 10, gray.shape[0])
            cmin = max(px - 10, 0)
            cmax = min(px + 10, gray.shape[1])
            region = gray[rmin:rmax, cmin:cmax]
            if region.size == 0:
                continue

            mean_brightness = np.mean(region)
            # 임계값으로 흑/백/빈칸 구분
            if mean_brightness > 200:
                state[row_idx, col_idx] = -1  # 백
            elif mean_brightness < 50:
                state[row_idx, col_idx] = 1   # 흑
            else:
                state[row_idx, col_idx] = 0   # 빈칸

    # 돌 좌표 리스트 추출
    black_stones = np.argwhere(state == 1).tolist()
    white_stones = np.argwhere(state == -1).tolist()

    # (옵션) 결과 시각화
    if show_result:
        # 원본 이미지에 교차점 찍기 (빨간점)
        for row in grid_centers:
            for (cx, cy) in row:
                cv2.circle(img, (int(cx), int(cy)), 3, (0, 0, 255), -1)
        cv2.imshow("Analyzed Omok Board (19x19)", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    start = (19 - 9) // 2  # 5
    end = start + 9  # 14

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


def main():
    image_path = "omokk2.jpg"  # 실제 이미지 파일 경로
    state, black_stones, white_stones = analyze_omok_board_19x19(
        image_path=image_path,
        show_result=True
    )
    print("State Array (19x19):")
    print(state)
    print("Black Stones:", black_stones)
    print("White Stones:", white_stones)


if __name__ == "__main__":
    main()
