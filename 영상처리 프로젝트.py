# 주제   : 여러 사람이 있는 영상에서, 원하는 인물을 드래그하여 지정하면 해당 인물만 트래킹한 영상을 따로 출력 및 저장한다.
# 사용법 : 코드를 실행한 후 첫 화면에서 인물의 상반신을 드래그한 후 스페이스 바를 누른다.
#           (단 재생 속도가 느리다)

import cv2
import numpy as np

# ***** 영상 읽기 *****
video_path = 'bts_dance.mp4'        # 소스코드와 같은 폴더 내에 위치한 영상파일 이름 작성.
cap = cv2.VideoCapture(video_path)  # 비디오(bts_dance.mp4)를 읽어들인다.

# ***** 결과 영상을 저장할 준비 *****
result_size = (375, 667)    # (가로, 세로), 저장하고자 하는 영상의 사이즈. 375 * 667로 지정해주면 핸드폰 화면에서 꽉 차게 보이는 사이즈이다.
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # mp4v 코덱으로 저장한다.
result = cv2.VideoWriter('%s_result.mp4' % (video_path.split('.')[0]), fourcc, cap.get(cv2.CAP_PROP_FPS), result_size)
# cv2.VideoWriter함수의 각 인자 설명: 결과 파일의 이름, 코덱, 초당 프레임 개수(원본 영상과 동일한 프레임으로), 영상 사이즈
                         
if not cap.isOpened():      # 만일 비디오가 열리지 않았을 경우 프로그램 종료.
    exit()


# ***** 관심 영역 선택 준비 *****
ret, img = cap.read()       # 추적할 인물(관심영역) 선택을 위해 첫 번째 프레임을 img에 읽어온다.

cv2.namedWindow('관심 인물을 선택하세요')
cv2.imshow('관심 인물을 선택하세요', img) # 첫번째 프레임 보여주기


# ***** 관심 영역 지정하기 *****
# 관심 영역을 지정하여 rect로 반환한다. fromCenter: 선택 영역이 센터에서 시작하지 않는다, showCrosshair: 중앙 십자선을 보여준다.
rect = cv2.selectROI('관심 인물을 선택하세요', img, fromCenter=False, showCrosshair=True)
cv2.destroyWindow('관심 인물을 선택하세요')


# ***** 트래커 세팅 *****
tracker = cv2.TrackerCSRT_create()  # csrt트래커를 생성한다.
                                    ## opencv에서 제공하는 Tracker에는 csrt외에도 6가지가 더 있지만,
                                    ## 정확도가 좋을수록 속도가 느리고, 속도를 빠르게 할수록 정확도가 떨어지기 때문에
                                    ## 정확도가 적절한 csrt를 사용하였다.
tracker.init(img, rect)             # 지정한 관심영역 rect를 추적하도록 명령하는 함수.
success, box = tracker.update(img)


# ************************* 지정한 인물 추적하기 *************************
while True:
    ret, img = cap.read()   # 비디오를 읽어서 img라는 변수에 저장을 한다.

    if not ret:             # 비디오를 잘못 읽었거나 비디오가 종료되었을 경우 프로그램 종료.
        exit()

# ***** 트래커 업데이트 *****
    success, box = tracker.update(img)
    # while문에서 매 프레임을 읽어올 때마다, 사용자가 지정한 영역과 새로운 프레임(img)과 비교하여 따라가도록 업데이트 해준다.
    # success: update성공 여부를 boolean으로 반환. box: 따라간 부분의 영역에 대한 데이터를 배열로 반환.


# ***** box안에 담긴 정보 가져오기 *****
    left, top, width, height = [int(v) for v in box]
    # for v in box: box안에 담긴 데이터 수 만큼 반복하면서, 한 반복마다 해당 데이터를 v에 담는다.
    # int(v): v값을 integer로 변환.
    # left, top, width, height(왼쪽, 맨위, 너비, 높이)순서로 저장.


# ***** box의 중심 구하기 ***** (구하는 이유: box 중심을 기준으로 result_size만큼 영상을 자르기 위해)
    center_x = left + width/2   # x축 중심 구하기. (0, 0)좌표는 좌측 최상단 이므로 left(왼쪽)에서 너비의 반 만큼 더한다.
    center_y = top + height/2   # y축 중심 구하기. top(맨위)에서 높이의 반 만큼 더한다.


# ***** box의 중심을 기준으로 결과영상 자르기 *****
    result_top = int(center_y - result_size[1] / 2)     # top: y축 중심에서 결과영상의 높이(result_size[1])의 반 만큼 뺀다.
    result_bottom = int(center_y + result_size[1] / 2)  # bottom: y축 중심에서 결과영상의 높이(result_size[1])의 반 만큼 더한다.
    result_left = int(center_x - result_size[0] / 2)    # left: x축 중심에서 결과영상의 너비(result_sizep[0])의 반 만큼 뺀다.
    result_right = int(center_x + result_size[0] / 2)   # right: x축 중심에서 결과영상의 너비(result_sizep[0])의 반 만큼 더한다.

    result_img = img[result_top:result_bottom, result_left:result_right].copy() # 최종 이미지(프레임). [top부터 bottom까지, left부터 right까지]
    # 밑에서 cv2.rectangle로 img에 사각형 그림을 그려주고 있기 때문에, 결과 영상에까지 사각형이 그려지지 않게 하기위해 copy하여 저장한다.

    
# ***** 트래킹된 구역을 직사각형으로 나타내기 ***** (box에서 가져온 정보를 바탕으로 직사각형으로 나타내기)
    cv2.rectangle(img, pt1=(left, top), pt2=(left + width, top + height), color=(255, 0, 0), thickness=3)
    # cv2.rectangle 각 인자 설명: (그릴 이미지, 왼쪽 위 좌표(pt1), 오른쪽 아래 좌표(pt2), 사각형 색(파랑), 사각형 두께(3))

    cv2.imshow('result_img', result_img)    # 결과 프레임 출력
    cv2.imshow('img', img)                  # 원본 프레임 출력
    result.write(result_img)                # 결과 영상 저장
    if cv2.waitKey(1) == ord('q'):          # q를 누르면 종료
        break
    
cap.release()
result.release()
cv2.destroyAllWindows()
