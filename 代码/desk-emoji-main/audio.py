import time
import pygame
import speech_recognition as sr
import os
from concurrent.futures import ThreadPoolExecutor

from common import *


class Listener(object):

    def __init__(self, gpt=None):
        self.recognizer = sr.Recognizer()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.gpt = gpt

    def hear(self, audio_path="input.wav", timeout=8):
        try:
            with sr.Microphone() as source:
                print("开始说话...")
                audio_data = self.recognizer.listen(source, timeout=timeout)
                print("录音已完成")
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(audio_data.get_wav_data())
                return self.gpt.speech(audio_path=audio_path)

        except Exception as e:
            error(e, "Speech recognition Failed")


class Speaker(object):
    def __init__(self, gpt=None):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.gpt = gpt
        self.pygame_initialized = False  # 新增标志位，用于记录pygame是否已初始化
        self.audio_path = ""  # 新增属性，用于记录当前音频文件路径，便于初始化操作

    def _init_pygame(self):
        if not self.pygame_initialized:
            pygame.mixer.init()
            self.pygame_initialized = True

    def _play_audio(self, audio_path, callback=None):
        try:
            self._init_pygame()  # 先确保pygame已初始化
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            self.audio_path = audio_path  # 记录当前播放的音频文件路径
            while pygame.mixer.music.get_busy():
                time.sleep(1)
            if callback:
                callback(audio_path)
            # 以下为修改后的初始化相关逻辑，重置音频文件路径等相关状态，准备下次使用
            self.audio_path = ""  
            self.pygame_initialized = False
            pygame.mixer.music.unload()  # 卸载当前音乐资源，进行初始化操作
            pygame.mixer.quit()
            pygame.mixer.init()
            self.pygame_initialized = True
            time.sleep(2)
        except pygame.error as e:
            error(e, "Audio playback failed")

    def say(self, text="", voice="onyx", audio_path="output.mp3"):
        try:
            self.gpt.speak(text=text, voice=voice, audio_path=audio_path)
            self.executor.submit(self._play_audio, audio_path)
        except Exception as e:
            error(e, "Speak Failed")


if __name__ == "__main__":
    from gpt import *
    llm = GPT()
    llm.connect()
    # listener = Listener(llm)
    # print(listener.hear())
    speaker = Speaker(llm)
    speaker.say(text="你好呀")