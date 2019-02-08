# -*- coding: utf-8 -*-
from gtts import gTTS
import os.path
import re
import random
import os
import vlc

ttsfilename="/tmp/say.mp3"

#Text to speech converter with translation
# 텍스트를 소리로 변환시켜주는 함수
def say(words):
    # 문자열을 한국어로 읽어준다.
    # 파일에 저장하고 그 파일을 읽어 들임
    tts = gTTS(text=words, lang="ko")
    tts.save(ttsfilename)
    os.system("mpg123 "+ttsfilename)
    os.remove(ttsfilename)

comWord = "" # 끝말잇기 구글 어시스턴트가 말할 단어
f = open("word.txt", 'r')
lines = f.readlines()
wlist = list()
for line in lines:
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+') # 읽은 문자열에서 한글만 추출한다
    line = hangul.sub('', line)
    # 2글자 이상인 단어만 저장한다.
    if(len(line) >= 2):
        wlist.append(line)
f.close()
wlist.sort()

def game(phrase):
    global wlist    # 단어 리스트
    global comWord  # 끝말잇기 구글 어시스턴트가 말할 단어

    # 게임 시작 시
    if (phrase == 'game_play'):
        i = random.randrange(1,len(wlist))
        comWord = wlist[i] # 랜덤으로 단어 하나를 정한다
        say("끝말잇기를 시작합니다.")
        print("끝말잇기를 시작합니다.")
        say("처음 단어는 " + comWord + "입니다.")
        print("처음 단어는 " + comWord + "입니다.")
        return True # 게임 시작 
    
    # 게임 중지 시
    elif (phrase == "중지"):
        say("끝말잇기를 중지합니다. 안녕")
        print("끝말잇기를 중지합니다. 안녕")
        return False # 게임 중지
    
    # 사용자가 말한 단어를 추출함
    phrase = phrase.split("'")[3]
    print("당신의 단어 : " + phrase)
    say("당신의 단어 : " + phrase)

    # 만약 말하지 않거나 끝말이 이어지지 않으면 사용자가 진다
    if(len(phrase) <= 0):
        say("제 승리입니다. 하하 바보 자식")   
        print("제 승리입니다. 하하 바보 자식")
        return False
    
    elif (phrase[0] != comWord[len(comWord) - 1]):
        say("제 승리입니다. 하하 바보 자식")   
        print("제 승리입니다. 하하 바보 자식")
        return False
    
    # 어시스턴트가 끝말이 이어지는 단어를 찾는다.
    else:
        isComLose = True # 어시스턴트가 졌는지 판단하는 변수
        for w in wlist:
            if(w[0] == phrase[len(phrase) - 1]):
                comWord = w
                isComLose = False
                say("다음 단어는" + comWord + "입니다.")
                print("다음 단어는 " + comWord + "입니다.")
                return True # 게임은 계속
        
        if isComLose: # 어시스턴트가 짐
            say("제가 졌습니다. ㅜㅜ")
            print("제가 졌습니다. ㅜㅜ")
            return False # 게임 끝


# 각 감정에 따라 음악을 재생하는 함수
def music_play(phrase):
    music_path = "" # 음악 파일 위치 
    # 슬픈 경우
    if phrase == 'sad_music':
        # 음악 폴더 경로
        path_dir = '/home/pi/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/library/sad'
        file_list = os.listdir(path_dir)
        file_list.sort()
        i = random.randrange(1,len(file_list))
        # 랜덤하게 음악 파일을 하나 고른다.
        music_path = str(os.path.join(path_dir, file_list[i]))

        # 음악 재생
        p = vlc.MediaPlayer(music_path)
        p.play()
        
        say("슬프지 마세요. 저도 슬퍼요. 제가 음악을 들려 드릴게요")
        print("슬프지 마세요. 저도 슬퍼요. 제가 음악을 들려 드릴게요")
        return True
    
    # 행복한 경우
    elif phrase == 'happy_music':
        # 음악 폴더 경로
        path_dir = '/home/pi/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/library/happy'
        file_list = os.listdir(path_dir)
        file_list.sort()
        i = random.randrange(1,len(file_list))
        # 랜덤하게 음악 파일을 하나 고른다.
        music_path = str(os.path.join(path_dir, file_list[i]))

        # 음악 재생
        p = vlc.MediaPlayer(music_path)
        p.play()
        say("저도 행복해요! 제 마음을 담은 음악이에요!")
        print("저도 행복해요! 제 마음을 담은 음악이에요!")
        return True
    
    # 화난 경우
    elif phrase == 'angry_music':
        # 파일 경로
        path_dir = '/home/pi/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/library/angry'
        file_list = os.listdir(path_dir)
        file_list.sort()
        i = random.randrange(1,len(file_list))
        # 랜덤하게 파일 하나를 고름

        # 음악 재생
        music_path = str(os.path.join(path_dir, file_list[i]))
        p = vlc.MediaPlayer(music_path)
        p.play()
        say("화날 땐 이 음악을 들으면서 진정하시는 건 어떠신가요? ")
        print("화날 땐 이 음악을 들으면서 진정하시는 건 어떠신가요? ")
        return True
    

    
