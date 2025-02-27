import cv2
import numpy as np

def rectify_omok_board(image_path, output_path="rectified_board.jpg"):
    """
    rectify_omok_board(image_path : str, output_path : str) -> return None : None
    ----------------------------------------------------------------------------
    1) 이미지를 로드하고 그레이스케일 + 에지(Canny) 검출
    2) 가장 큰 사각형(바둑판 테두리)을 찾기 위해 윤곽선(Contour) 검색
    3) 사각형 꼭짓점 4개를 approxPolyDP로 구한 뒤, 시계/반시계 방향으로 재정렬
    4) cv2.getPerspectiveTransform() + cv2.warpPerspective()로 정면에 맞게 보정
    5) 보정된 이미지를 output_path에 저장
    """
    # 1) 이미지 로드
    original = cv2.imread(image_path)
    if original is None:
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {image_path}")

    # 크기가 너무 크면 작업 부담이 크므로 적절히 리사이즈(예: 가로 기준 1000px)
    scale = 1000 / original.shape[1] if original.shape[1] > 1000 else 1
    if scale < 1:
        original = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # 2) 그레이스케일 + 블러 + 에지 검출
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)   # 노이즈 완화
    edges = cv2.Canny(gray, 50, 150)

    # 3) 윤곽선 검색
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("윤곽선(Contour)을 찾을 수 없습니다.")

    # 4) 가장 큰 사각형 찾기 (바둑판 테두리를 가정)
    max_area = 0
    board_corners = None

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)  # 윤곽선 근사 정확도
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:  # 사각형(꼭짓점 4개)
            area = cv2.contourArea(approx)
            if area > max_area:
                max_area = area
                board_corners = approx

    if board_corners is None:
        raise ValueError("사각형 형태의 바둑판 테두리를 찾지 못했습니다.")

    # 5) 사각형 꼭짓점 좌표를 float32 형태로 변환
    pts = board_corners.reshape(-1, 2).astype(np.float32)

    # 6) 꼭짓점 순서(시계방향 또는 반시계방향) 정렬 함수
    def reorder_points(points):
        # x+y가 가장 작은 점 → 좌상단, 가장 큰 점 → 우하단
        # x-y가 양수면 우측, 음수면 좌측 등에 응용
        # 혹은 좀 더 일반적으로 정렬하기 위해 아래와 같이 사용
        # 1) y + x 합이 작은 순(좌상), 큰 순(우하)
        # 2) y - x가 음수면 우상, 양수면 좌하
        rect = np.zeros((4, 2), dtype=np.float32)

        # 합과 차
        s = points.sum(axis=1)
        diff = np.diff(points, axis=1)

        rect[0] = points[np.argmin(s)]     # 좌상단
        rect[2] = points[np.argmax(s)]     # 우하단
        rect[1] = points[np.argmin(diff)]  # 우상단
        rect[3] = points[np.argmax(diff)]  # 좌하단
        return rect

    # 꼭짓점 정렬
    ordered_pts = reorder_points(pts)

    # 7) 목표 영상 크기 설정 (가령 600x600으로 warp)
    #    실제 바둑판 19x19를 고려해 여유있게 600~700 정도로 설정
    size = 600
    dst_pts = np.float32([
        [0, 0],
        [size, 0],
        [size, size],
        [0, size]
    ])

    # 8) 퍼스펙티브 변환 행렬 계산
    M = cv2.getPerspectiveTransform(ordered_pts, dst_pts)
    warped = cv2.warpPerspective(original, M, (size, size))

    # 결과 저장
    cv2.imwrite(output_path, warped)
    print(f"정면 보정된 이미지를 저장했습니다: {output_path}")

    # 디버그 용도로 확인하기
    # cv2.imshow("Original", original)
    # cv2.imshow("Rectified Board", warped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    input_path = "omokk2.jpg"
    output_path = "rectified_omok.jpg"
    rectify_omok_board(input_path, output_path)
