#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import argparse
import json
import os.path
import pathlib2 as pathlib
import RPi.GPIO as GPIO # 하드웨어 조작 용

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

from action import * # 커스텀 액션을 모아 놓은 파일

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

# led 핀 번호
yellow_pin = 13
green_pin = 19
red_pin = 26

# led 및 스위치 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(yellow_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(red_pin, GPIO.OUT)

GPIO.output(yellow_pin, False)
GPIO.output(green_pin, False)
GPIO.output(red_pin, False)
isgame = False
ismusic = False

WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""

# 각 이벤트때 행동을 보여주는 함수
def process_event(event, assistant):
    global isgame

    # 대화가 시작 됨
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        # start listening talk
        # yellow on
        GPIO.output(yellow_pin, True)
        GPIO.output(green_pin, False)
        GPIO.output(red_pin, False)
        # 끝말잇기 게임 중
        if isgame:
            print("당신의 차례입니다.")
            say("당신의 차례입니다.")
        # 평상시
        else:
            print()

    print(event)

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        print()
    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in event.actions:
            print('Do command', command, 'with params', str(params))
    
    # 대화가 정상적으로 끝남
    # green on
    if event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        GPIO.output(yellow_pin, False)
        GPIO.output(green_pin, True)
        GPIO.output(red_pin, False)
        if isgame:
            #talk again
            # 끝말잇기 게임을 계속함
            assistant.start_conversation()
        else:
            # 평상 시 바로 대화 종료함
            print("byebye")
            say("대화를 중지합니다.")
        print()
    
    # 대화가 비정상적으로 끝남
    # red on
    if event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
        GPIO.output(yellow_pin, False)
        GPIO.output(green_pin, False)
        GPIO.output(red_pin, True)
        assistant.stop_conversation()
    
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--device-model-id', '--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=False,
                        help='the device model ID registered with Google')
    parser.add_argument('--project-id', '--project_id', type=str,
                        metavar='PROJECT_ID', required=False,
                        help='the project ID used to register this device')
    parser.add_argument('--device-config', type=str,
                        metavar='DEVICE_CONFIG_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'googlesamples-assistant',
                            'device_config_library.json'
                        ),
                        help='path to store and read device configuration')
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='path to store and read OAuth2 credentials')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    device_model_id = None
    last_device_id = None
    try:
        with open(args.device_config) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args.device_model_id and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (
        args.device_model_id and args.device_model_id != device_model_id)

    device_model_id = args.device_model_id or device_model_id

    with Assistant(credentials, device_model_id) as assistant:
        events = assistant.start()

        device_id = assistant.device_id
        print('device_model_id:', device_model_id)
        print('device_id:', device_id + '\n')
        
        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args.project_id:
                register_device(args.project_id, credentials,
                                device_model_id, device_id)
                pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                    exist_ok=True)
                with open(args.device_config, 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)
        # 구글 어시스턴트가 정상적으로 실행됨
        print("start!")
       
        # 언제든지 스위치를 눌렀을 때 대화를 할 수 있도록 함
        def my_callback(channel):
            print("button Pressed")
            assistant.start_conversation()
        
        # 이벤트 함수 - 스위치가 눌렀을 경우에만 실행
        GPIO.add_event_detect(25, GPIO.RISING, callback=my_callback)
                
        for event in events:
            # 이벤트를 시작함
            process_event(event, assistant)
            usrcmd = event.args
            
            global isgame # 끝말 잇기 게임 판단
            global ismusic # 음악 재생 판단
            
            # 끝말잇기 게임 중일 때 
            if isgame and not str(usrcmd).find("with_follow_on_turn") >= 0 and not usrcmd == None:
                # 중지를 하지 않으면 커스텀 액션이 실행되지 않고 구글 어시스턴트 원래 기능이 실행됨
                assistant.stop_conversation() 
                print("okok")
                isgame = game(str(usrcmd)) # 사용자가 말한 낱말을 보낸다
                                   
            # 끝말잇기 게임 시작
            if '끝말잇기'.lower() in str(usrcmd).lower():
               assistant.stop_conversation()
               isgame = game('game_play')
            
            # 사용자가 각 감정을 말했을 때 음악을 재생하도록 함
            if '슬퍼'.lower() in str(usrcmd).lower() or '슬프다' in str(usrcmd):
               assistant.stop_conversation()
               ismusic= music_play('sad_music')
            
            if '행복해'.lower() in str(usrcmd).lower() or '행복하다'.lower() in str(usrcmd).lower():
               assistant.stop_conversation()
               ismusic= music_play('happy_music')
            
            if '화나'.lower() in str(usrcmd).lower() or '화난다' in str(usrcmd) or '화가 나' in str(usrcmd):
               assistant.stop_conversation()
               ismusic= music_play('angry_music')
               
            
if __name__ == '__main__':
    main()
