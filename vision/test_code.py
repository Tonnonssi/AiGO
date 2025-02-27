import cv2
import numpy as np
import time

def take_photo(cam_num=0, output_file='omok.jpg'):
    """
    take_photo(filename : str) -> return filename : str
    -----------------------------------------------
    웹캠으로부터 사진을 캡처한 후, 이미지를 저장하고 파일명을 반환합니다.
    """
    cap = cv2.VideoCapture(cam_num)  # 0: 기본 웹캠
    output_file='omok.jpg'

    if not cap.isOpened():
        raise IOError("웹캠을 열 수 없습니다.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Webcam (Press SPACE to capture, ESC to exit)", frame)

        key = cv2.waitKey(1) & 0xFF
        # - 32 = SPACE, 27 = ESC

        if key == 32:  # SPACE
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{output_file}"
            cv2.imwrite(filename, frame)
            print(f"Captured: {filename}")

        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return filename


def apply_lens_distortion(image_path, output_path, exp=0.98, scale=1):
    """
    apply_lens_distortion(image_path : str, output_path : str, exp : float, scale : float) -> return None : None
    ---------------------------------------------------------------------------------------------
    이미지를 오목·볼록 렌즈 효과로 왜곡하여 저장합니다.

    - image_path : 입력 이미지 경로
    - output_path : 왜곡된 이미지를 저장할 경로
    - exp : 왜곡 지수 (볼록 : 1.1 이상, 오목 : 0.1 ~ 1)
    - scale : 왜곡 적용 영역의 범위 (0 ~ 1)

    이미지가 왜곡된 결과물을 파일로 저장하며, 현재 함수 안에서는 결과를 cv2.imshow로 표시합니다.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise IOError("이미지를 불러올 수 없습니다: " + image_path)

    rows, cols = img.shape[:2]

    # 매핑 배열 생성
    mapy, mapx = np.indices((rows, cols), dtype=np.float32)

    # 좌표 정규화
    mapx = 2 * mapx / (cols - 1) - 1
    mapy = 2 * mapy / (rows - 1) - 1

    # 직교좌표를 극 좌표로 변환
    r, theta = cv2.cartToPolar(mapx, mapy)

    # 왜곡 영역 적용
    r[r < scale] = r[r < scale] ** exp

    # 극 좌표를 직교좌표로 변환
    mapx, mapy = cv2.polarToCart(r, theta)

    # 좌상단 기준으로 좌표 재변환
    mapx = ((mapx + 1) * cols - 1) / 2
    mapy = ((mapy + 1) * rows - 1) / 2

    # 재매핑 변환
    distorted = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    # 왜곡된 이미지 저장
    cv2.imwrite(output_path, distorted)

    # 로컬에서 결과 확인(윈도우 창으로)
    cv2.imshow("Distorted Image", distorted)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def crop_board_from_image(image_path, output_path):
    """
    crop_board_from_image(image_path : str, output_path : str) -> return None : None
    --------------------------------------------------------------------------------
    입력 이미지에서 바둑판(혹은 특정 사각형 영역)을 찾아내어 크롭한 뒤 저장합니다.

    - image_path : 입력 이미지 경로
    - output_path : 크롭된 이미지를 저장할 경로

    크롭된 결과물을 파일로 저장하며, 로컬 환경에선 cv2.imshow로 결과를 확인합니다.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise IOError("이미지를 불러올 수 없습니다: " + image_path)

    

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges_refined = cv2.Canny(blurred, 30, 100)
    contours_refined, _ = cv2.findContours(edges_refined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    board_contour_refined = None
    max_area_refined = 0

    for contour in contours_refined:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:  # 사각형
            area = cv2.contourArea(approx)
            if area > max_area_refined:
                max_area_refined = area
                board_contour_refined = approx

    if board_contour_refined is None:
        raise ValueError("바둑판(사각형) 윤곽을 찾을 수 없습니다.")

    # x, y, w, h = cv2.boundingRect(board_contour_refined)
    cropped_board_refined = image[135:375, 260:500]
    cropped_board_refined = cv2.rotate(cropped_board_refined, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite(output_path, cropped_board_refined)

    cv2.imshow("Cropped Board", cropped_board_refined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def main():
    # 1) 사진 촬영 (웹캠에서 사진 캡처)
    filename = take_photo()

    # 2) 왜곡 보정 적용
    #distorted_output = "omokk2.jpg"
    #apply_lens_distortion(filename, distorted_output, exp=0.94, scale=1)

    # 3) 바둑판 크롭
    cropped_output = "omokk3.jpg"
    crop_board_from_image(filename, cropped_output)


if __name__ == "__main__":
    main()

