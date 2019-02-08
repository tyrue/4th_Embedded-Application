
# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys
import cv2
import io
import os

# 구글 스피치
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types 

# 구글 비전
from google.cloud import vision
from google.cloud.vision import types as typesV

import pyaudio
from six.moves import queue

cam = cv2.VideoCapture(-1)

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        # 음성 인식 텍스트의 공백을 제거하고, 모두 소문자로 변경하여 검색 효율을 높인다.
        transcript = result.alternatives[0].transcript
        transcript = transcript.replace(" ", "")
        transcript = transcript.lower()
        

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        # 음성 인식과 동시에 실행
        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)
            
        # 음성 인식이 끝난 후 실행
        else:
            print(transcript + overwrite_chars)
            landSearch(transcript) # 현재 폴더에 저장된 이미지에 있는 랜드마크 검색
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0

# 랜드 마크 검색
def landSearch(trans):
    client = vision.ImageAnnotatorClient()

    path_dir = './'; # 현재 폴더
    file_list = os.listdir(path_dir) # 현재 폴더에 저장된 모든 파일 리스트

    for item in file_list: # 파일리스트 전체 검색
        if item.find('jpg') is not -1:  # 파일중 jpg형식인 파일만 검색
            with io.open('./' + item, 'rb') as image_file:
                content = image_file.read()

            image = typesV.Image(content=content)
            response = client.landmark_detection(image=image)
            landmarks = response.landmark_annotations # 랜드마크 검색

            for landmark in landmarks: # 랜드마크 검색 결과 리스트
                # 랜드마크 검색 결과 텍스트의 공백을 제거하고, 모두 소문자로 변경하여 검색 효율을 높인다.
                landmark.description = landmark.description.replace(" ", "")
                landmark.description = landmark.description.lower()
                #print("landmark : " + landmark.description)
                
                # 음성인식 결과와 랜드마크 검색 결과를 비교하여 일치하면 해당하는 이미지를 출력한다.
                if landmark.description.find(trans) is not -1: 
                    img = cv2.imread(item, cv2.IMREAD_COLOR) 
                    cv2.namedWindow(item, cv2.WINDOW_NORMAL) # 윈도우 창을 변경 가능으로 설정
                    cv2.resizeWindow(item, 640, 640) # 창의 크기를 640, 640으로 변경
                    cv2.imshow(item, img) # 이미지 출력
                    cv2.waitKey(0)
                    return 0
                
    print("No search landmarks")
            # [END vision_python_migration_landmark_detection]
                

    
def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == '__main__':
    main()
# [END speech_transcribe_streaming_mic]
