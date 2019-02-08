import RPi.GPIO as GPIO
import time
import cv2
import datetime
import io

# 구글 비전 
from google.cloud import vision 		
from google.cloud.vision import types

led_anger = 13 		# led 핀
led_joy = 19
led_surprise = 26

# 각 핀의 IO설정을 한다.
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(led_anger, GPIO.OUT)
GPIO.setup(led_joy, GPIO.OUT)
GPIO.setup(led_surprise, GPIO.OUT)

GPIO.output(led_anger, False) 	# 각 핀의 전압이 없는 상태로 초기화 한다.
GPIO.output(led_joy, False)
GPIO.output(led_surprise, False)

cam = cv2.VideoCapture(-1) # 첫 번째로 연결된 카메라

def button(): 		# 버튼을 눌렀을 경우 실행되는 함수
    state = False
    if GPIO.input(12) == 0: # 스위치가 눌렀을 때, 상태를 바꾼다.
        state = True
        print("button press")
    return state

def camera(): 		# 카메라가 실행되는 함수
    try:
        while True:
            ret, img = cam.read()	# 카메라 영상
            cv2.imshow('Cam', img)	# 카메라를 보여준다.
                        key = cv2.waitKey(10)
            if key == ord('x'):		# x키를 눌렀을 경우 윈도우가 꺼진다
            	cam.release()
            	cv2.destroyAllWindows()
            	GPIO.cleanup()
            	break

            if button() == True: 		# 버튼이 눌렀을 경우, 현재 영상을 이미지 파일로 저장
                filename = getDatetime() + '.jpg' # 현재 시간으로 파일 이름을 저장
                cv2.imwrite(filename , img)
                time.sleep(0.5)
                detect_label(filename)
		
    except KeyboardInterrupt:	# 키보드 인터럽트 시 윈도우를 끈다.
        cam.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()

def getDatetime():	# 현재 시간을 계산하는 함수
# 연, 월, 일, 시, 분, 초를 계산한다.
    date = datetime.datetime.now()
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    hour = str(date.hour)
    min = str(date.minute)
    sec = str(date.second)

    if int(month) < 10: 
        month = '0' + month
    if int(day) < 10:
        day = '0' + day
    if int(hour) < 10:
        hour = '0' + hour
    if int(min) < 10:
        min = '0' + min

    t =  year + month + day + hour + min + sec
    return t
    
    def detect_label(path):	# 이미지안의 사람 얼굴을 인식하는 함수
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content) # 이미지를 불러들어온다.
    
    response2 = client.face_detection(image=image) # 이미지 속의 얼굴을 인식한다.
    faces = response2.face_annotations # 얼굴의 표정을 분석한다.
        
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY') # 표정에 대한 점수
    print('Faces:')

    for face in faces:
        if face.anger_likelihood > 2:	# 만약 화난 표정의 점수가 3이상이면, 빨간 led를 비춘다.
            print("anger")
            GPIO.output(led_anger, True)            
            GPIO.output(led_joy, False)
            GPIO.output(led_surprise, False)
            
        elif face.joy_likelihood > 2: 	# 만약 웃는 표정의 점수가 3이상이면, 녹색 led를 비춘다.
            print("joy")
            GPIO.output(led_joy, True)
            GPIO.output(led_surprise, False)
            GPIO.output(led_anger, False)
            
        elif face.surprise_likelihood > 2: 	# 만약 놀란 표정의 점수가 3이상이면, 노랑 led를 비춘다.
            print("surprise")
            GPIO.output(led_surprise, True)
            GPIO.output(led_anger, False)
            GPIO.output(led_joy, False)
            
	# 각 표정에 대한 분석 결과를 출력한다.
        print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
        print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
        print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))
        
if __name__ == '__main__':
    camera()