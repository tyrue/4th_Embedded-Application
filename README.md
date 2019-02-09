# 임베디드 응용 및 실습(Embedded-Application)

## 1. 과제들-Assignments

### (1) 개요

과목을 수행하면서 만들었던 프로젝트들이다. 라즈베리파이를 이용했으며, Google vision, Google speech, Open-CV를 이용하였다.



### (2) 실행 화면

#### 1) Assignment1 - **얼굴 감정 인식 장치 만들기** 

![image](https://user-images.githubusercontent.com/20302410/52472183-ffbb3c80-2bd5-11e9-8a23-6900b3ec01af.png)

Open-CV와  Google-Vision을 이용했다. 스위치를 눌러 pi 카메라로 사진을 찍으면, 

사진 분석 결과에서 joy가 VERY_LIKELY가 나왔을 때, 19핀에 연결 된 녹색 LED가 켜진다.



#### 2) Assignment2 - **음성 인식 카메라 만들기**

![image](https://user-images.githubusercontent.com/20302410/52472582-faaabd00-2bd6-11e9-8c0e-c315349e3bdd.png)

Google-Speech와 Google-Vision, Open-CV를 이용하였다. 

영어로 take a picture라고 말을하면, pi카메라로 사진을 찍고 그 사진을 분석한다.

캡처 사진 결과로 기술, 전자기기 등 휴대폰의 특징을 묘사하는 라벨이 출력되었다.



#### 3) Assignment3 - 이미지에서 랜드마크 검색

![image](https://user-images.githubusercontent.com/20302410/52472327-5a549880-2bd6-11e9-935b-0bb656a9bfaf.png)

Google-Speech와 Google-Vision, Open-CV를 이용하였다. 찾고 싶은 랜드마크를 마이크에 말을 하면, 이미지 폴더에 미리 저장된 이미지들을 분석하고, 그에 알맞는 사진을 띄워준다.

마추픽추라고 질문했을 때, landmark 검색 결과로 마추픽추에 해당하는 이미지를 출력한다.



## 2. 텀프로젝트-term project

### (1) 개요

수업 텀 프로젝트로 Google Assistant를 이용한 인공지능 스피커를 제작하였다. 기존의 Google Assistant에 커스텀한 기능을 추가하였다. 추가한 기능은 다음과 같다. 

1. 음성 인식 상태에 따라 led로 보여주기
2. 스위치를 눌러 대화 가능하게 하기
3. 끝말잇기 게임 구현
4. 자신의 감정을 말하면 그에 적절한 음악을 재생함

사용한 장비는 라즈베리파이, led, 스위치, 마이크이다.

### (2) 주요 코드

#### 1) 음성 인식 상태에 따라 led로 보여주기

![image](https://user-images.githubusercontent.com/20302410/52515363-c4645080-2c5d-11e9-837a-90e92ed06a98.png)

이벤트 타입이 ON_CONVERSATION_TURN_STARTED이면, 대화를 들을 준비가 됨을 뜻한다. 이 때 노란 LED를 킨다. 

이벤트 타입이 ON_CONVERSATION_TURN_FINISHED이면 대화가 정상적으로 끝남을 뜻한다. 이 때는 초록 LED를 킨다. 

이벤트 타입이 ON_CONVERSATION_TURN_TIMEOUT이면 대화가 비정상적으로 끝남을 뜻한다. 이 때는 빨강 LED를 킨다. 



#### 2) 스위치를 눌러 대화 가능하게 하기

![image](https://user-images.githubusercontent.com/20302410/52515409-87e52480-2c5e-11e9-91ff-42a889fa47aa.png)

메인 메소드에서 장치 id와 모델 id를 모두 정상적으로 입력 받으면 정상적으로 실행이 된다.  

언제든지 스위치를 눌렀을 경우 대화 하기 위해, 대화 메소드인 

assistant.start_conversation()을 GPIO.add_event_detect 메소드로 콜백 한다.



#### 3) 끝말잇기 게임 구현

![image](https://user-images.githubusercontent.com/20302410/52515550-73a22700-2c60-11e9-95b4-3e31b96d326f.png)

event.args에는 사용자가 말한 음성이 배열로 저장되어있다. isgame변수는 현재 끝말잇기 게임 중인지 판단하고, ismusic은 음악이 현재 재생되어 있는지 판단한다. 

커스텀 액션을 실행할 때는 처음에 stop_conversation()을 호출해야 하는데,  그 이유는 사용자의 질문에 대해 미리 저장된 Google Assistant의 답변을 하기 때문이다.  그래서 대화를 중지 시키고, 커스텀 액션 메소드를 호출하는 방법을 사용한다.



![image](https://user-images.githubusercontent.com/20302410/52515626-75b8b580-2c61-11e9-8955-61998bfe82ee.png)

커스텀 액션을 저장한 파일이다. 여기서 커스텀 액션 답변을 해줘야 하기 때문에 Google TTS를 사용하였다. 

끝말잇기에 사용할 단어는 word.txt에 저장되어 있다. 이 파일을 읽어들여 배열에 저장하고, 랜덤하게 단어를 선택한다. 



![image](https://user-images.githubusercontent.com/20302410/52515651-f5df1b00-2c61-11e9-843b-51ae99827d65.png)

사용자가 중지를 말하면 게임은 중단 된다. 사용자가 답변을 하지 못했거나, 잘못된 답변을 하면 패배 메세지를 말한다. 만약 제대로 된 답변을 했다면 다음 단어를 랜덤하게 고른다. 



#### 4) 자신의 감정을 말하면 그에 적절한 음악을 재생함

![image](https://user-images.githubusercontent.com/20302410/52515692-638b4700-2c62-11e9-8511-e8cbd64883f9.png)

사용자가 각 감정을 말했을 때, 그에 따른 커스텀 액션 메소드를 호출한다.



![image](https://user-images.githubusercontent.com/20302410/52515693-66863780-2c62-11e9-9de0-7a016a670c62.png)

사용자가 슬픈 감정을 말했을 경우, 각 감정 폴더에 저장된 음악 파일을 임의로 선택해서 재생한다.



### (3) 실행 화면

![image](https://user-images.githubusercontent.com/20302410/52515735-d4326380-2c62-11e9-8048-4701c47fdb92.png)



![image](https://user-images.githubusercontent.com/20302410/52515736-d8f71780-2c62-11e9-9ef2-1b127b38bed1.png)



![image](https://user-images.githubusercontent.com/20302410/52515738-dbf20800-2c62-11e9-8264-6e0f6ea934f4.png)

